import logging
import os
import psutil
from socket import gethostname
import sys
from time import sleep
from typing import Dict, Set, Tuple

from libmuscle.native_instantiator.process_manager import ProcessManager
from libmuscle.native_instantiator.agent.map_client import MAPClient
from libmuscle.native_instantiator.agent.agent_commands import (
        CancelAllCommand, ShutdownCommand, StartCommand)
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources


_logger = logging.getLogger(__name__)


class Agent:
    """Runs on a compute node and starts processes there."""
    def __init__(self, node_name: str, server_location: str) -> None:
        """Create an Agent.

        Args:
            node_name: Name (hostname) of this node
            server_location: MAP server of the manager to connect to
        """
        _logger.info(f'Agent at {node_name} starting')

        self._process_manager = ProcessManager()

        self._node_name = node_name

        _logger.info(f'Connecting to manager at {server_location}')
        self._server = MAPClient(self._node_name, server_location)
        _logger.info('Connected to manager')

    def run(self) -> None:
        """Execute commands and monitor processes."""
        _logger.info('Reporting resources')
        self._server.report_resources(self._inspect_resources())

        shutting_down = False
        while not shutting_down:
            command = self._server.get_command()
            if isinstance(command, StartCommand):
                _logger.info(f'Starting process {command.name}')
                _logger.debug(f'Args: {command.args}')
                _logger.debug(f'Env: {command.env}')

                self._process_manager.start(
                        command.name, command.work_dir, command.args, command.env,
                        command.stdout, command.stderr)
            elif isinstance(command, CancelAllCommand):
                _logger.info('Cancelling all instances')
                self._process_manager.cancel_all()

            elif isinstance(command, ShutdownCommand):
                # check that nothing is running
                shutting_down = True
                _logger.info('Agent shutting down')

            finished = self._process_manager.get_finished()
            if finished:
                for name, exit_code in finished:
                    _logger.info(f'Process {name} finished with exit code {exit_code}')
                self._server.report_result(finished)

            sleep(0.1)

    def _inspect_resources(self) -> OnNodeResources:
        """Inspect the node to find resources and report on them.

        The terminology for identifying processors gets very convoluted, with Linux,
        Slurm, OpenMPI and IntelMPI all using different terms, or sometimes the same
        terms for different things. See the comment in planner/resources.py for what is
        what and how we use it.

        Returns:
            A dict mapping resource types to resource descriptions.
        """
        if hasattr(os, 'sched_getaffinity'):
            hwthreads_by_core_tuple: Dict[Tuple[int, int], Set[int]] = dict()

            # these are the logical hwthread ids that we can use
            hwthread_ids = list(os.sched_getaffinity(0))

            for hwthread_id in hwthread_ids:
                topdir = f'/sys/devices/system/cpu/cpu{hwthread_id}/topology'
                with open(f'{topdir}/core_id', 'r') as f:
                    # this gets the logical core id for the hwthread
                    core_id = int(f.read())
                with open(f'{topdir}/physical_package_id', 'r') as f:
                    # this gets the die/socket id for the hwthread
                    package_id = int(f.read())

                core_tuple = (package_id, core_id)
                hwthreads_by_core_tuple.setdefault(core_tuple, set()).add(hwthread_id)

            core_lgid_hwthreads = [
                    (i, hwthreads_by_core_tuple[core_tuple])
                    for i, core_tuple in enumerate(
                        sorted(hwthreads_by_core_tuple.keys()))]

            cores = CoreSet((
                    Core(core_lgid, hwthreads)
                    for core_lgid, hwthreads in core_lgid_hwthreads))

        else:
            # MacOS doesn't support thread affinity, but older Macs with Intel
            # processors do have SMT. Getting the hwthread to core mapping is not so
            # easy, and if we're running on macOS then we're not on a cluster and don't
            # do binding anyway. So we're going to get the number of hwthreads and the
            # number of cores here, and synthesise a mapping that may be wrong, but will
            # at least represent the number of cores and threads per core correctly.
            nhwthreads = psutil.cpu_count(logical=True)
            ncores = psutil.cpu_count(logical=False)

            if nhwthreads is None:
                if ncores is not None:
                    _logger.warning(
                            'Could not determine number of hwthreads, assuming no SMT')
                    nhwthreads = ncores
                else:
                    _logger.warning(
                            'Could not determine CPU configuration, assuming a single'
                            ' core')
                    ncores = 1
                    nhwthreads = 1
            elif ncores is None:
                _logger.warning(
                        'Could not determine number of cores, assuming no SMT')
                ncores = nhwthreads

            hwthreads_per_core = nhwthreads // ncores

            if ncores * hwthreads_per_core != nhwthreads:
                # As far as I know, there are no Macs with heterogeneous SMT, like in
                # the latest Intel CPUs.
                _logger.warning(
                        'Only some cores seem to have SMT, core ids are probably'
                        ' wrong. If this is a cluster then this will cause problems,'
                        ' please report an issue on GitHub and report the machine and'
                        ' what kind of OS and hardware it has. If we\'re running on a'
                        ' local machine, then this won\'t affect the run, but I\'d'
                        ' still appreciate an issue, because it is unexpected for sure.'
                        )

            cores = CoreSet((
                    Core(
                        cid,
                        set(range(
                            cid * hwthreads_per_core, (cid + 1) * hwthreads_per_core))
                        )
                    for cid in range(ncores)
                    ))

        resources = OnNodeResources(self._node_name, cores)
        _logger.info(f'Found resources: {resources}')
        return resources


def configure_logging(node_name: str, log_level: int) -> None:
    """Make us output logs to a custom log file."""
    fmt = '%(asctime)s %(levelname)s %(message)s'
    formatter = logging.Formatter(fmt)

    handler = logging.FileHandler(f'muscle3_agent_{node_name}.log', mode='w')
    handler.setFormatter(formatter)

    # Find and remove default handler to disable automatic console output
    # Testing for 'stderr' in the stringified version is not nice, but
    # seems reliable, and doesn't mess up pytest's caplog mechanism while
    # it also doesn't introduce a runtime dependency on pytest.
    logging.getLogger().handlers = [
            h for h in logging.getLogger().handlers
            if 'stderr' not in str(h)]

    logging.getLogger().addHandler(handler)

    logging.getLogger().setLevel(log_level)


if __name__ == '__main__':
    node_name = gethostname()
    server_location = sys.argv[1]
    log_level = int(sys.argv[2])

    configure_logging(node_name, log_level)

    agent = Agent(node_name, server_location)
    agent.run()
