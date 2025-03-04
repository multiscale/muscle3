import logging
from pathlib import Path
from subprocess import Popen, TimeoutExpired
import sys
from threading import Lock
from time import sleep
from typing import Dict, List, Tuple

from libmuscle.native_instantiator.agent.agent_commands import (
        CancelAllCommand, StartCommand, ShutdownCommand)
from libmuscle.native_instantiator.iagent_manager import IAgentManager
from libmuscle.native_instantiator.map_server import MAPServer
from libmuscle.native_instantiator.global_resources import global_resources
from libmuscle.planner.resources import OnNodeResources, Resources


_logger = logging.getLogger(__name__)


class AgentManager(IAgentManager):
    """Manage the node agents.

    Each node of our allocated resources gets an agent, which launches and monitors
    processes or that node. This class launches those agents across the nodes,
    and communicates with them.

    The AgentManager sits in between the NativeInstantiator and the MAPServer. It gets
    called by NativeInstantiator with requests for resources and commands to start and
    cancel processes on nodes, and it gets called by MAPServer with requests from the
    agents.
    """
    def __init__(self, agent_dir: Path) -> None:
        """Create an AgentManager.

        Create the object, then launch the agents and wait for them to connect and send
        information about the available resources.

        Args:
            agent_dir: Directory in which agents can write log files.
        """
        self._expected_nodes = global_resources().nodes
        self._nodes: Dict[str, str] = dict()
        self._resources: Resources = Resources([])
        self._resources_lock = Lock()   # protects _nodes and _resources

        self._finished_processes: List[Tuple[str, int]] = list()
        self._finished_processes_lock = Lock()

        self._server = MAPServer(self)
        self._launch_agents(agent_dir, self._server.get_location())

    def get_resources(self) -> Resources:
        """Return detected resources.

        This returns a list of sets of logical hwthread ids per core, per node.

        Called by NativeInstantiator.
        """
        # no need to lock, _resources is already in its final state
        return self._resources

    def start(
            self, node_name: str, name: str, work_dir: Path, args: List[str],
            env: Dict[str, str], stdout: Path, stderr: Path) -> None:
        """Start a process on a node.

        The files that the output is directed to will be overwritten if they already
        exist.

        Args:
            node_name: Name of the node to run the process on
            name: Name under which this process will be known
            work_dir: Working directory in which to start
            args: Executable and arguments to run
            env: Environment variables to set
            stdout: File to redirect stdout to
            stderr: File to redirect stderr to
        """
        agent_hostname = self._nodes[node_name]
        command = StartCommand(name, work_dir, args, env, stdout, stderr)
        self._server.deposit_command(agent_hostname, command)

    def cancel_all(self) -> None:
        """Cancel all processes.

        This tells the agents to stop all running processes they've started.

        Called by NativeInstantiator.
        """
        for node_host_name in self._nodes.values():
            self._server.deposit_command(node_host_name, CancelAllCommand())

    def get_finished(self) -> List[Tuple[str, int]]:
        """Returns names and exit codes of finished processes.

        This returns all processes that have finished running since the previous call;
        each started process will be returned exactly once. The names are the ones
        passed to start().

        Called by NativeInstantiator.
        """
        with self._finished_processes_lock:
            next_batch = self._finished_processes
            self._finished_processes = list()

        return next_batch

    def shutdown(self) -> None:
        """Shut down the manager and its agents."""
        command = ShutdownCommand()
        for node_host_name in self._nodes.values():
            self._server.deposit_command(node_host_name, command)

        try:
            self._agents_process.wait(60)
        except TimeoutExpired:
            _logger.warning(
                    'Agents did not shut down within one minute, sending signal...')
            self._agents_process.kill()

        try:
            self._agents_process.wait(10)
            self._agents_stdout.close()
            self._agents_stderr.close()
        except TimeoutExpired:
            _logger.warning('Agents still not down, continuing shutdown anyway.')

        self._server.stop()

    def report_resources(self, resources: OnNodeResources) -> None:
        """Report resources found on a node.

        Called by MAPServer from a server thread.

        Args:
            resources: Description of a node's resources
        """
        _logger.debug(f'Agent reported {resources}')

        # The agent reports a hostname, which we assume contains the node name
        agent_hostname = resources.node_name
        for exp_node_name in self._expected_nodes:
            if exp_node_name in resources.node_name:
                resources.node_name = exp_node_name
                break
        else:
            _logger.warning(
                    f'Agent reported hostname {resources.node_name}, which could not'
                    ' be matched against any expected node name from'
                    f' {self._expected_nodes}.')

        with self._resources_lock:
            self._nodes[resources.node_name] = agent_hostname
            self._resources.add_node(resources)

    def report_result(self, names_exit_codes: List[Tuple[str, int]]) -> None:
        """Report results of finished processes.

        Called by MAPServer from a server thread.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        with self._finished_processes_lock:
            self._finished_processes.extend(names_exit_codes)

    def _launch_agents(self, agent_dir: Path, server_location: str) -> None:
        """Actually launch the agents.

        This runs a local process, either to start a single agent locally, or on a
        cluster to start all of them in one go.

        Args:
            agent_dir: Working directory for the agents
            server_location: MAPServer network location string for the agents to
                connect to
        """
        _logger.info('Launching MUSCLE agents...')

        python = sys.executable
        if not python:
            raise RuntimeError(
                    'Could not launch agents because sys.executable is not set.')

        log_level = logging.getLogger('libmuscle').getEffectiveLevel()

        args = [
                sys.executable, '-m', 'libmuscle.native_instantiator.agent',
                server_location, str(log_level)]

        args = global_resources().agent_launch_command(args)

        self._agents_stdout = (agent_dir / 'agent_launch.out').open('a')
        self._agents_stderr = (agent_dir / 'agent_launch.err').open('a')

        _logger.debug(f'Launching agents using {args}')
        self._agents_process = Popen(
                args, cwd=agent_dir, stdout=self._agents_stdout,
                stderr=self._agents_stderr)

        num_expected = len(self._expected_nodes)

        resources_complete = False
        while not resources_complete:
            sleep(0.1)
            with self._resources_lock:
                resources_complete = len(self._nodes) == num_expected
                too_many_agents = len(self._nodes) > num_expected

            _logger.debug(f'{len(self._nodes)} agents up of {num_expected}')

            if self._agents_process.poll() is not None:
                msg = (
                        'Agents unexpectedly stopped running. This is not supposed'
                        ' to happen. Please see the agent log for more information,'
                        ' and please file an issue on GitHub.')
                _logger.error(msg)
                raise RuntimeError(msg)

            if too_many_agents:
                msg = (
                        'More agents were started than MUSCLE3 asked for. This is not'
                        ' supposed to happen. Please file an issue on GitHub, with the'
                        ' SLURM version (use "sbatch -V") and the sbatch command used'
                        ' to submit the job.')
                _logger.error(msg)
                raise RuntimeError(msg)

        _logger.info(f'All agents running on {self._nodes}')
