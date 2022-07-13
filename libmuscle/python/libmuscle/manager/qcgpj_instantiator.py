import asyncio
import logging
import multiprocessing as mp
import os
from pathlib import Path
import queue
import sys
import traceback
from typing import Dict, List, Tuple

from qcg.pilotjob.allocation import (
        Allocation as qcg_Allocation, NodeAllocation as qcg_NodeAllocation)
from qcg.pilotjob.config import Config as qcg_Config
from qcg.pilotjob.errors import InternalError as qcg_InternalError
from qcg.pilotjob.executor import Executor as qcg_Executor
from qcg.pilotjob.joblist import (
        Job as qcg_Job, JobExecution as qcg_JobExecution,
        JobResources as qcg_JobResources)
from qcg.pilotjob.manager import (
        SchedulingIteration as qcg_SchedulingIteration,
        SchedulingJob as qcg_SchedulingJob)
from qcg.pilotjob.parseres import get_resources as qcg_get_resources
from qcg.pilotjob.resources import (
        Node as qcg_Node, ResourcesType as qcg_ResourcesType)

from ymmsl import ExecutionModel, MPICoresResReq, Reference, ThreadedResReq

from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, InstantiationRequest, Process,
        ProcessStatus, QueueingLogHandler, ShutdownRequest)
from libmuscle.planner.planner import Resources


_logger = logging.getLogger(__name__)


class StateTracker:
    """Tracks processes and their state.

    This keeps a list of running processes and their state. It
    receives callbacks from QCG-PJ when the state of a job changes,
    and updates the list accordingly.

    Attributes:
        processes: Dict mapping instance names to Process objects.
    """
    def __init__(self) -> None:
        """Create a StateTracker."""
        self.processes = dict()     # type: Dict[Reference, Process]

        # These are for communicating with QCG-PJ
        self.queued_to_execute = 0
        self.stop_processing = False
        self.zmq_address = ''

    # QCG-PJ callbacks
    def job_executing(self, job_iteration: qcg_SchedulingIteration) -> None:
        """Called by Executor when a job has started to run.

        Args:
            job_iteration: The job iteration that has started
        """
        name = job_iteration._scheduling_job.job.name
        self.processes[name].status = ProcessStatus.RUNNING
        _logger.debug(f'Job {name} running')

    def job_finished(
            self, job_iteration: qcg_SchedulingIteration,
            allocation: qcg_Allocation,
            exit_code: int, error_msg: str, canceled: bool) -> None:
        """Called by executor when a job has finished.

        Args:
            job_iteration: The job iteration that has finished
            allocation: The allocation it ran on
            exit_code: Its exit code
            error_msg: Its error message
            canceled: Whether it was canceled
        """
        name = job_iteration._scheduling_job.job.name
        process = self.processes[name]
        if canceled:
            process.status = ProcessStatus.CANCELED
        elif exit_code == 0:
            process.status = ProcessStatus.SUCCESS
        else:
            process.status = ProcessStatus.ERROR

        process.exit_code = exit_code
        process.error_msg = error_msg


class QCGPJInstantiator(mp.Process):
    """Background process for interacting with the QCG-PJ executor."""
    def __init__(
            self, resources: mp.Queue, requests: mp.Queue, results: mp.Queue,
            log_records: mp.Queue, run_dir: Path) -> None:
        """Create a QCGPJProcessManager.

        Args:
            resources: Queue for returning the available resources
            requests: Queue to take requests from
            results: Queue to communicate finished processes over
            log_messages: Queue to push log messages to
        """
        super().__init__(name='QCGPJProcessManager')
        self._resources_out = resources
        self._requests_in = requests
        self._results_out = results
        self._log_records_out = log_records
        self._run_dir = run_dir

    def run(self) -> None:
        """Entry point for the process."""
        # Put QCG-PJ output in run dir
        # The configuration setting below is ignored by the agents
        # due to a bug in QCG-PJ
        qcgpj_dir = self._run_dir / 'qcgpj'
        qcgpj_dir.mkdir(exist_ok=True)
        os.chdir(qcgpj_dir)

        self._reconfigure_logging()

        # Executor needs to be instantiated before we go async
        qcg_config = {
                qcg_Config.AUX_DIR: str(qcgpj_dir)}     # type: Dict[str, str]
        self._qcg_resources = qcg_get_resources(qcg_config)
        self._state_tracker = StateTracker()
        self._executor = qcg_Executor(
                self._state_tracker, qcg_config, self._qcg_resources)

        self._send_resources()

        try:
            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._main())
        except:     # noqa
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)
            self._results_out.put(CrashedResult())

    async def _main(self) -> None:
        """Main function for the background process.

        This sets up QCG-PJ and then accepts requests for instantiating
        jobs, stopping them, or shutting down. Results of finished jobs
        are returned via the results queue.
        """
        qcg_iters = dict()  # type: Dict[Reference, qcg_SchedulingIteration]

        shutting_down = False
        done = False
        while not done:
            while not shutting_down:
                try:
                    request = self._requests_in.get_nowait()
                    if isinstance(request, ShutdownRequest):
                        _logger.debug('Got ShutdownRequest')
                        self._state_tracker.stop_processing = True
                        shutting_down = True

                    elif isinstance(request, CancelAllRequest):
                        _logger.debug('Got CancelAllRequest')
                        await self._cancel_all(qcg_iters)
                        _logger.debug('Done CancelAllRequest')

                    elif isinstance(request, InstantiationRequest):
                        if not shutting_down:
                            qcg_alloc, qcg_iter = self._create_job(
                                    request, self._qcg_resources.rtype)
                            qcg_iters[request.instance] = qcg_iter
                            self._state_tracker.processes[request.instance] = (
                                    Process(
                                        request.instance, request.resources))
                            self._state_tracker.queued_to_execute += 1
                            await self._executor.execute(qcg_alloc, qcg_iter)

                except queue.Empty:
                    break

            await asyncio.sleep(0.1)

            for name, process in list(self._state_tracker.processes.items()):
                if process.status.is_finished():
                    _logger.debug(f'Reporting {name} done')
                    self._results_out.put(process)
                    del self._state_tracker.processes[name]

            if shutting_down:
                _logger.debug(f'Done: {self._state_tracker.processes}')
                done = len(self._state_tracker.processes) == 0

        _logger.debug('Stopping executor')
        await self._executor.stop()

    def _reconfigure_logging(self) -> None:
        """Reconfigure logging to send to log_records_out."""
        root_logger = logging.getLogger()
        for h in list(root_logger.handlers):
            root_logger.removeHandler(h)

        handler = QueueingLogHandler(self._log_records_out)
        root_logger.addHandler(handler)

    def _send_resources(self) -> None:
        """Converts and sends QCG available resources."""
        resources = Resources()
        for node in self._qcg_resources.nodes:
            resources.cores[node.name] = set(map(int, node.free_ids))

        self._resources_out.put(resources)

    async def _cancel_all(
            self, qcg_iters: Dict[Reference, qcg_SchedulingIteration]) -> None:
        """Cancels all running jobs."""
        # Repeat cancel until they're gone to work around QCG-PJ
        # race condition.
        while any([
                not p.status.is_finished()
                for p in self._state_tracker.processes.values()]):

            for instance, process in self._state_tracker.processes.items():
                if process.status.is_finished():
                    continue

                qcg_iter = qcg_iters[instance]
                try:
                    await self._executor.cancel_iteration(
                            qcg_iter.job, qcg_iter.iteration)
                    _logger.debug(f'Canceled {instance}')
                except qcg_InternalError:
                    _logger.debug(f'Canceled {instance} not found')
                    raise
                except AttributeError:
                    # Workaround for QCG-PJ bug
                    _logger.debug(f'Canceled {instance} not found')
                    raise
            await asyncio.sleep(0.1)

    def _create_job(
            self, request: InstantiationRequest,
            qcg_resources_type: qcg_ResourcesType
            ) -> Tuple[qcg_Allocation, qcg_SchedulingIteration]:
        """Creates a QCG allocation and job for a request."""
        total_cores = sum(map(len, request.resources.cores.values()))

        env = self._create_env(request.instance, request.implementation.env)

        if request.implementation.script:
            execution = self._qcg_job_execution_with_script(request, env)
        else:
            execution = self._qcg_job_execution_normal(
                    request, env, qcg_resources_type)

        resources = qcg_JobResources(numCores=total_cores)

        qcg_job = qcg_Job(
                str(request.instance),
                execution=execution,
                resources=resources)

        qcg_allocation = qcg_Allocation()
        for node_name, cores in request.resources.cores.items():
            qcg_cores = [str(i) for i in cores]
            qcg_allocation.add_node(
                    qcg_NodeAllocation(qcg_Node(node_name), qcg_cores, {}))

        sjob = qcg_SchedulingJob(self._state_tracker, qcg_job)
        qcg_iteration = qcg_SchedulingIteration(sjob, None, None, None, [])
        return qcg_allocation, qcg_iteration

    def _create_env(
            self, instance: Reference, overlay: Dict[str, str]
            ) -> Dict[str, str]:
        """Updates the environment with the implementation's env.

        This updates env in-place. Keys from overlay that start with
        + will have the corresponding value appended to the matching
        (by key, without the +) value in env, otherwise the value in
        env gets overwritten.
        """
        env = os.environ.copy()
        env['MUSCLE_INSTANCE'] = str(instance)

        for key, value in overlay.items():
            if key.startswith('+'):
                if key[1:] in env:
                    env[key[1:]] += value
                else:
                    env[key[1:]] = value
            else:
                env[key] = value
        return env

    def _qcg_job_execution_with_script(
            self, request: InstantiationRequest, env: Dict[str, str]
            ) -> qcg_JobExecution:
        """Create a JobExecution with a run script."""
        impl = request.implementation
        if impl.script is None:
            raise RuntimeError()

        script_file = request.instance_dir / 'run_script.sh'
        with script_file.open('w') as f:
            f.write(impl.script)
        script_file.chmod(0o700)

        if isinstance(request.res_req, ThreadedResReq):
            env['MUSCLE_THREADS'] = str(request.res_req.threads)
        elif isinstance(request.res_req, MPICoresResReq):
            # OpenMPI support
            rank_file = request.instance_dir / 'rankfile'
            with rank_file.open('w') as f:
                i = 0
                for node, cores in request.resources.cores.items():
                    for c in sorted(cores):
                        f.write(f'rank {i}={node} slot={c}\n')
                        i += 1
            env['MUSCLE_OPENMPI_RANK_FILE'] = str(rank_file)

            # IntelMPI support
            mpi_res_args = list()
            for node, cores in request.resources.cores.items():
                mpi_res_args.extend(['-host', node, '-n', str(len(cores))])
            env['MUSCLE_INTELMPI_RESOURCES'] = ' '.join(mpi_res_args)

            # General environment
            env['MUSCLE_MPI_PROCESSES'] = str(
                    request.res_req.mpi_processes)
            env['MUSCLE_THREADS_PER_MPI_PROCESS'] = str(
                    request.res_req.threads_per_mpi_process)

        return qcg_JobExecution(
                exec=str(script_file),
                env=env,
                stdout=str(request.stdout_path),
                stderr=str(request.stderr_path),
                wd=str(request.work_dir),
                model='default')

    def _qcg_job_execution_normal(
            self, request: InstantiationRequest, env: Dict[str, str],
            qcg_resources_type: qcg_ResourcesType) -> qcg_JobExecution:
        """Create a JobExecution for a normal description."""
        impl = request.implementation
        total_cores = sum(map(len, request.resources.cores.values()))

        if impl.execution_model == ExecutionModel.DIRECT:
            env['OMP_NUM_THREADS'] = str(total_cores)
        else:
            env['OMP_NUM_THREADS'] = '1'

        model_map = {
                ExecutionModel.DIRECT: 'threads',
                ExecutionModel.OPENMPI: 'openmpi',
                ExecutionModel.INTELMPI: 'intelmpi',
                ExecutionModel.SRUNMPI: 'srunmpi'}
        qcg_execution_model = model_map[impl.execution_model]

        executable = str(impl.executable)
        args = impl.args if impl.args is not None else []
        if qcg_resources_type == qcg_ResourcesType.LOCAL:
            if impl.execution_model == ExecutionModel.DIRECT:
                if not impl.virtual_env and not impl.modules:
                    # QCG-PJ uses a bash call like this in all but this
                    # case, so we add it here to be consistent.
                    cmd = ' '.join([executable] + args)
                    executable = 'bash'
                    args = ['-l', '-c', cmd]
            elif impl.execution_model == ExecutionModel.OPENMPI:
                executable, args = self._with_local_open_mpi(
                        executable, args, total_cores)
            elif impl.execution_model == ExecutionModel.INTELMPI:
                executable, args = self._with_local_intel_mpi(
                        executable, args, total_cores)
            elif impl.execution_model == ExecutionModel.SRUNMPI:
                raise RuntimeError(
                    f'Cannot instantiate implementation {impl.name} with'
                    ' execution model "srunmpi", because there is no'
                    ' Slurm/srun here.')

        _logger.debug(f'Starting {executable} with {args}')

        return qcg_JobExecution(
                exec=executable,
                args=args,
                env=env,
                stdout=str(request.stdout_path),
                stderr=str(request.stderr_path),
                modules=impl.modules,
                venv=str(impl.virtual_env) if impl.virtual_env else None,
                wd=str(request.work_dir),
                model=qcg_execution_model)

    def _with_local_open_mpi(
            self, executable: str, args: List[str], num_processes: int
            ) -> Tuple[str, List[str]]:
        """Create OpenMPI mpirun call."""
        new_args = ['-n', str(num_processes), executable]
        new_args.extend(args)
        return 'mpirun', new_args

    def _with_local_intel_mpi(
            self, executable: str, args: List[str], num_processes: int
            ) -> Tuple[str, List[str]]:
        """Create IntelMPI mpirun call."""
        new_args = ['-n', str(num_processes), executable]
        new_args.extend(args)
        return 'mpirun', new_args
