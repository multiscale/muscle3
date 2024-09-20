import logging
import multiprocessing as mp
from os import chdir
from pathlib import Path
import queue
import sys
from time import sleep
import traceback
from typing import Dict, List, Optional

from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, create_instance_env, InstantiationRequest,
        Process, ProcessStatus, reconfigure_logging, ShutdownRequest)
from libmuscle.native_instantiator.process_manager import ProcessManager
from libmuscle.native_instantiator.resource_detector import ResourceDetector
from libmuscle.native_instantiator.run_script import make_script, prep_resources
from libmuscle.planner.planner import Resources
from ymmsl import MPICoresResReq, MPINodesResReq, ResourceRequirements, ThreadedResReq


_logger = logging.getLogger(__name__)


class NativeInstantiator(mp.Process):
    """Instantiates instances on the local machine."""
    def __init__(
            self, resources: mp.Queue, requests: mp.Queue, results: mp.Queue,
            log_records: mp.Queue, run_dir: Path) -> None:
        """Create a NativeInstantiator

        Args:
            resources: Queue for returning the available resources
            requests: Queue to take requests from
            results: Queue to communicate finished processes over
            log_messages: Queue to push log messages to
            run_dir: Run directory for the current run
        """
        super().__init__(name='NativeInstantiator')
        self._resources_out = resources
        self._requests_in = requests
        self._results_out = results
        self._log_records_out = log_records
        self._run_dir = run_dir

        self._resource_detector = ResourceDetector()
        self._process_manager = ProcessManager()
        self._processes: Dict[str, Process] = dict()

    def run(self) -> None:
        """Entry point for the process"""
        try:
            m3_dir = self._run_dir / 'muscle3'
            m3_dir.mkdir(exist_ok=True)
            chdir(m3_dir)

            reconfigure_logging(self._log_records_out)
            self._send_resources()
            self._main()

        except:     # noqa
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)
            self._resources_out.put(CrashedResult())
            self._results_out.put(CrashedResult())

    def _main(self) -> None:
        """Main function for the background process.

        This accepts requests for instantiating jobs, stopping them, or shutting down.
        Results of finished jobs are returned via the results queue.
        """
        shutting_down = False
        done = False
        while not done:
            while not shutting_down:
                try:
                    request = self._requests_in.get_nowait()
                    if isinstance(request, ShutdownRequest):
                        _logger.debug('Got ShutdownRequest')
                        shutting_down = True

                    elif isinstance(request, CancelAllRequest):
                        _logger.debug('Got CancelAllRequest')
                        self._process_manager.cancel_all()
                        _logger.debug('Done CancelAllRequest')

                    elif isinstance(request, InstantiationRequest):
                        if not shutting_down:
                            self._instantiate(request)

                except queue.Empty:
                    break

            self._report_failed_processes()
            self._report_finished_processes()

            if shutting_down:
                _logger.debug(f'Done: {self._processes}')
                done = not self._processes

            if not done:
                sleep(0.1)

    def _send_resources(self) -> None:
        """Detect resources and report them to the manager."""
        resources = Resources()

        res = zip(self._resource_detector.nodes, self._resource_detector.cores_per_node)
        for node, num_cores in res:
            resources.cores[node] = set(range(num_cores))

        self._resources_out.put(resources)

    def _instantiate(self, request: InstantiationRequest) -> None:
        """Instantiate an implementation according to the request."""
        name = str(request.instance)

        env = create_instance_env(request.instance, request.implementation.env)
        self._add_resources(env, request.res_req)

        rankfile: Optional[Path] = None
        if self._resource_detector.on_cluster():
            _logger.debug('On cluster...')
            rankfile_contents, resource_env = prep_resources(
                  request.implementation.execution_model, request.resources)

            _logger.debug(f'Rankfile: {rankfile_contents}')
            _logger.debug(f'Resource env: {resource_env}')

            if rankfile_contents:
                rankfile = self._write_rankfile(request, rankfile_contents)

            if resource_env:
                env.update(resource_env)

        # env['MUSCLE_THREADS_PER_MPI_PROCESS'] = str(
        #         request.res_req.threads_per_mpi_process)
        # env['MUSCLE_OPENMPI_RANK_FILE'] = str(rank_file)
        # env['MUSCLE_INTELMPI_RESOURCES'] = ' '.join(mpi_res_args)

        run_script_file = self._write_run_script(request, rankfile)
        args = [str(run_script_file)]

        self._processes[name] = Process(request.instance, request.resources)

        try:
            self._process_manager.start(
                    name, request.work_dir, args, env,
                    request.stdout_path, request.stderr_path)
            self._processes[name].status = ProcessStatus.RUNNING

        except Exception as e:
            self._processes[name].status = ProcessStatus.ERROR
            self._processes[name].error_msg = f'Instance failed to start: {e}'

    def _write_rankfile(self, request: InstantiationRequest, rankfile: str) -> Path:
        """Create and write out the rankfile and return its location.

        Also known as a machinefile or hostfile depending on the MPI implementation.
        """
        rankfile_file = request.instance_dir / 'rankfile'

        with rankfile_file.open('w') as f:
            f.write(rankfile)

        return rankfile_file

    def _write_run_script(
            self, request: InstantiationRequest, rankfile: Optional[Path]) -> Path:
        """Create and write out the run script and return its location."""
        if request.implementation.script:
            run_script = request.implementation.script
        else:
            run_script = make_script(
                    request.implementation, request.res_req,
                    not self._resource_detector.on_cluster(), rankfile)

        run_script_file = request.instance_dir / 'run_script.sh'

        with run_script_file.open('w') as f:
            f.write(run_script)

        run_script_file.chmod(0o700)
        return run_script_file

    def _add_resources(
            self, env: Dict[str, str], res_req: ResourceRequirements) -> None:
        """Add resource env vars to the given env."""
        if isinstance(res_req, ThreadedResReq):
            num_threads = res_req.threads
        elif isinstance(res_req, (MPICoresResReq, MPINodesResReq)):
            num_threads = res_req.threads_per_mpi_process

        env['MUSCLE_THREADS'] = str(num_threads)
        env['OMP_NUM_THREADS'] = str(num_threads)

        num_mpi_processes: Optional[int] = None
        if isinstance(res_req, MPICoresResReq):
            num_mpi_processes = res_req.mpi_processes
        elif isinstance(res_req, MPINodesResReq):
            num_mpi_processes = res_req.nodes * res_req.mpi_processes_per_node

        if num_mpi_processes is not None:
            env['MUSCLE_MPI_PROCESSES'] = str(num_mpi_processes)

    def _report_failed_processes(self) -> None:
        """Get processes that failed to start and report their status."""
        failed_processes: List[str] = list()

        for name, process in self._processes.items():
            if process.status == ProcessStatus.ERROR:
                self._results_out.put(process)
                failed_processes.append(name)

        for name in failed_processes:
            del self._processes[name]

    def _report_finished_processes(self) -> None:
        """Get finished processes and report back their status."""
        for name, exit_code in self._process_manager.get_finished():
            process = self._processes[name]
            if process.status == ProcessStatus.RUNNING:
                if exit_code == 0:
                    process.status = ProcessStatus.SUCCESS
                else:
                    process.status = ProcessStatus.ERROR
                    process.error_msg = 'Instance returned a non-zero exit code'
            process.exit_code = exit_code
            self._results_out.put(process)
            del self._processes[name]
