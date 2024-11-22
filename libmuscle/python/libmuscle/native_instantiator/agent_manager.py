import logging
from pathlib import Path
from subprocess import Popen, TimeoutExpired
import sys
from threading import Lock
from time import sleep
from typing import Any, Dict, FrozenSet, List, Tuple

from libmuscle.native_instantiator.agent.agent_commands import (
        CancelAllCommand, StartCommand, ShutdownCommand)
from libmuscle.native_instantiator.iagent_manager import IAgentManager
from libmuscle.native_instantiator.map_server import MAPServer
from libmuscle.native_instantiator.global_resources import global_resources


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
        self._nodes: List[str] = list()
        self._resources: Dict[str, Dict[str, Any]] = dict()
        self._resources_lock = Lock()   # protects _nodes and _resources

        self._finished_processes: List[Tuple[str, int]] = list()
        self._finished_processes_lock = Lock()

        self._server = MAPServer(self)

        _logger.info('Launching MUSCLE agents...')
        self._agents_process = self._launch_agents(
                agent_dir, self._server.get_location())

        expected_nodes = global_resources.nodes

        resources_complete = False
        while not resources_complete:
            sleep(0.1)
            with self._resources_lock:
                resources_complete = len(self._nodes) == len(expected_nodes)
            _logger.debug(f'{len(self._nodes)} agents up of {len(expected_nodes)}')

            if self._agents_process.poll() is not None:
                msg = (
                        'Agents unexpectedly stopped running. This is not supposed'
                        ' to happen. Please see the agent log for more information,'
                        ' and please file an issue on GitHub.')
                _logger.error(msg)
                raise RuntimeError(msg)

        _logger.info(f'All agents running on {self._nodes}')

        if sorted(expected_nodes) != sorted(self._nodes):
            _logger.error(
                    'Agent-reported node hostnames do not match what we got from the'
                    ' resource manager.')
            _logger.error(
                    'According to the resource manager, we have'
                    f' {sorted(expected_nodes)}')
            _logger.error(
                    f'The agents are reporting {sorted(self._nodes)}')

    def get_resources(self) -> Dict[str, List[FrozenSet[int]]]:
        """Return detected resources.

        This returns a list of tuples of logical hwthread ids for each core per node.

        Called by NativeInstantiator.
        """
        # no need to lock, _resources is already in its final state
        return {node_id: res['cpu'] for node_id, res in self._resources.items()}

    def start(
            self, node_id: str, name: str, work_dir: Path, args: List[str],
            env: Dict[str, str], stdout: Path, stderr: Path) -> None:
        """Start a process on a node.

        The files that the output is directed to will be overwritten if they already
        exist.

        Args:
            node_id: Id of the node to run the process on
            name: Name under which this process will be known
            work_dir: Working directory in which to start
            args: Executable and arguments to run
            env: Environment variables to set
            stdout: File to redirect stdout to
            stderr: File to redirect stderr to
        """
        command = StartCommand(name, work_dir, args, env, stdout, stderr)
        self._server.deposit_command(node_id, command)

    def cancel_all(self) -> None:
        """Cancel all processes.

        This tells the agents to stop all running processes they've started.

        Called by NativeInstantiator.
        """
        for node_id in self._nodes:
            self._server.deposit_command(node_id, CancelAllCommand())

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
        for node_id in self._nodes:
            self._server.deposit_command(node_id, command)

        try:
            self._agents_process.wait(60)
        except TimeoutExpired:
            _logger.warning(
                    'Agents did not shut down within one minute, sending signal...')
            self._agents_process.kill()

        try:
            self._agents_process.wait(10)
        except TimeoutExpired:
            _logger.warning('Agents still not down, continuing shutdown anyway.')

        self._server.stop()

    def report_resources(self, node_id: str, resources: Dict[str, Any]) -> None:
        """Report resources found on a node.

        Called by MAPServer from a server thread.

        Args:
            node_id: Id of the node these resources are on
            resources: Dict mapping resource type to resource ids
        """
        _logger.debug(f'Agent on {node_id} reported {resources}')
        with self._resources_lock:
            self._nodes.append(node_id)
            self._resources[node_id] = resources

    def report_result(self, names_exit_codes: List[Tuple[str, int]]) -> None:
        """Report results of finished processes.

        Called by MAPServer from a server thread.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        with self._finished_processes_lock:
            self._finished_processes.extend(names_exit_codes)

    def _launch_agents(self, agent_dir: Path, server_location: str) -> Popen:
        """Actually launch the agents.

        This runs a local process, either to start a single agent locally, or on a
        cluster to start all of them in one go.

        Args:
            agent_dir: Working directory for the agents
            server_location: MAPServer network location string for the agents to
                connect to
        """
        python = sys.executable
        if not python:
            raise RuntimeError(
                    'Could not launch agents because sys.executable is not set.')

        log_level = logging.getLogger('libmuscle').getEffectiveLevel()

        args = [
                sys.executable, '-m', 'libmuscle.native_instantiator.agent',
                server_location, str(log_level)]

        args = global_resources.agent_launch_command(args)

        _logger.debug(f'Launching agents using {args}')
        return Popen(args, cwd=agent_dir)
