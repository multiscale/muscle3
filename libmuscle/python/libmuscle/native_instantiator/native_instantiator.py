import logging
import multiprocessing as mp
from pathlib import Path
import queue
import sys
from time import sleep
import traceback
from typing import Dict, List, Optional

from libmuscle.errors import ConfigurationError
from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, create_instance_env, InstantiationRequest,
        Process, ProcessStatus, reconfigure_logging, ShutdownRequest)
from libmuscle.native_instantiator.agent_manager import AgentManager
from libmuscle.native_instantiator.global_resources import global_resources
from libmuscle.native_instantiator.run_script import make_script, prep_resources
from libmuscle.planner.resources import OnNodeResources, Resources
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

        self._processes: Dict[str, Process] = dict()

    def run(self) -> None:
        """Entry point for the process"""
        try:
            logs_dir = self._run_dir / 'logs'
            logs_dir.mkdir(exist_ok=True)

            self._agent_manager = AgentManager(logs_dir)

            reconfigure_logging(self._log_records_out)
            self._send_resources()
            self._main()

        except ConfigurationError as e:
            self._results_out.put(CrashedResult(e))

        except:     # noqa
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)

            result = CrashedResult(sys.exc_info()[1])
            self._resources_out.put(result)
            self._results_out.put(result)

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
                        self._agent_manager.cancel_all()

                    elif isinstance(request, InstantiationRequest):
                        _logger.debug('Got InstantiationRequest')
                        if not shutting_down:
                            self._instantiate(request)

                except queue.Empty:
                    break

            self._report_failed_processes()
            self._report_finished_processes()

            if shutting_down:
                _logger.debug(f'Remaining processes: {self._processes}')
                done = not self._processes

            if not done:
                sleep(0.1)

        self._agent_manager.shutdown()

    def _send_resources(self) -> None:
        """Detect resources and report them to the manager.

        We have potentially two sources of truth here: the Slurm environment variables
        and what the agents report based on what they're bound to. These should be
        consistent, but we check that and then try to be conservative to try to not
        step outside our bounds even if the cluster doesn't constrain processes to their
        assigned processors.
        """
        already_logged_smt = False
        resources = Resources()

        agent_res = self._agent_manager.get_resources()

        env_ncpus = dict(
                zip(global_resources().nodes, global_resources().logical_cpus_per_node)
                )

        for node_name in env_ncpus:
            if node_name not in agent_res.nodes():
                _logger.warning(
                        f'The environment suggests we should have node {node_name},'
                        ' but no agent reported running on it. We won''t be able'
                        ' to use this node.')
            else:
                env_nncpus = env_ncpus[node_name]
                ag_nncores = len(agent_res[node_name].cpu_cores)
                ag_nnthreads = len(list(agent_res[node_name].hwthreads()))

                if ag_nncores != ag_nnthreads and ag_nnthreads == env_nncpus:
                    if not already_logged_smt:
                        _logger.info(
                                'Detected SMT (hyperthreading) as available and'
                                ' enabled. Note that MUSCLE3 will assign whole cores to'
                                ' each thread or MPI process.')
                        already_logged_smt = True

                    resources.add_node(agent_res[node_name])

                elif ag_nncores < env_nncpus:
                    _logger.warning(
                            f'Node {node_name} should have {env_nncpus} cores'
                            f' available, but the agent reports only {ag_nncores}'
                            f' available to it. We\'ll use the {ag_nncores} we seem to'
                            ' have.')

                    resources.add_node(agent_res[node_name])

                elif env_nncpus < ag_nncores:
                    _logger.warning(
                            f'Node {node_name} should have {env_nncpus} cores'
                            f' available, but the agent reports {ag_nncores} available'
                            ' to it. Maybe the cluster does not constrain resources?'
                            f' We\'ll use the {env_nncpus} that we should have got.')
                    resources.add_node(
                            OnNodeResources(
                                node_name,
                                agent_res[node_name].cpu_cores.get_first_cores(
                                    env_nncpus)))

                else:
                    # no SMT, agent matches environment
                    resources.add_node(agent_res[node_name])

        for node in agent_res:
            if node.node_name not in env_ncpus:
                _logger.warning(
                        f'An agent is running on node {node.node_name} but the'
                        ' environment does not list it as ours. It seems that the'
                        ' node\'s hostname does not match what SLURM calls it. We will'
                        ' not use this node, because we\'re not sure it\'s really ours'
                        ' or if it is, how many resources on it we can use.'
                        )

        self._resources_out.put(resources)

    def _instantiate(self, request: InstantiationRequest) -> None:
        """Instantiate an implementation according to the request."""
        name = str(request.instance)

        env = create_instance_env(
                request.instance, request.implementation.base_env,
                request.implementation.env)
        self._add_resources(env, request.res_req)

        rankfile = request.instance_dir / 'rankfile'

        if global_resources().on_cluster():
            rankfile_contents, resource_env = prep_resources(
                  request.implementation.execution_model, request.resources,
                  rankfile)

            if rankfile_contents:
                with rankfile.open('w') as f:
                    f.write(rankfile_contents)
                env['MUSCLE_RANKFILE'] = str(rankfile)

            env.update(resource_env)

        run_script_file = self._write_run_script(request, rankfile)
        args = [str(run_script_file)]

        self._processes[name] = Process(request.instance, request.resources)

        _logger.debug(f'Instantiating {name} on {request.resources}')
        try:
            self._agent_manager.start(
                    request.resources.by_rank[0].node_name,
                    name, request.work_dir, args, env,
                    request.stdout_path, request.stderr_path)
            self._processes[name].status = ProcessStatus.RUNNING

        except Exception as e:
            _logger.warning(f'Instance {name} failed to start: {e}')
            self._processes[name].status = ProcessStatus.ERROR
            self._processes[name].error_msg = f'Instance failed to start: {e}'

    def _write_run_script(
            self, request: InstantiationRequest, rankfile: Optional[Path]) -> Path:
        """Create and write out the run script and return its location."""
        # TODO: Only write out once for each implementation
        if request.implementation.script:
            run_script = request.implementation.script
        else:
            run_script = make_script(
                    request.implementation, request.res_req,
                    request.work_dir, not global_resources().on_cluster(), rankfile)

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
        for name, exit_code in self._agent_manager.get_finished():
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
