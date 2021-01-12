from pathlib import Path
import logging
from typing import Optional

from ymmsl import PartialConfiguration

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.process_manager import ProcessManager
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.topology_store import TopologyStore


_logger = logging.getLogger(__name__)


class Manager:
    """The MUSCLE3 manager.

    This creates and manager instances and connects them together
    according to the simulation configuration.
    """
    def __init__(
            self,
            configuration: PartialConfiguration,
            run_dir: Optional[RunDir] = None
            ) -> None:
        """Create a Manager.

        This creates the manager and the associated server, but does
        not start any instances.

        Args:
            configuration: The simulation configuration.
            run_dir: Main working directory.
        """
        self._configuration = configuration
        self._run_dir = run_dir
        log_dir = self._run_dir.muscle_dir if self._run_dir else Path.cwd()
        self._logger = Logger(log_dir)
        self._topology_store = TopologyStore(configuration)
        self._process_manager = None    # type: Optional[ProcessManager]
        self._instance_registry = InstanceRegistry()
        self._server = MMPServer(
                self._logger, self._configuration.settings,
                self._instance_registry, self._topology_store)

    def get_server_location(self) -> str:
        """Returns the network location of the server."""
        return self._server.get_location()

    def start_instances(self) -> None:
        """Starts all required component instances."""
        if self._run_dir is None:
            raise RuntimeError('No run dir specified')
        configuration = self._configuration.as_configuration()
        self._process_manager = ProcessManager(configuration, self._run_dir)
        self._process_manager.start_all()

    def stop(self) -> None:
        """Shuts down the manager."""
        self._server.stop()

    def wait(self) -> None:
        """Blocks until the simulation is done, then shuts down."""
        if self._process_manager:
            self._process_manager.wait()
        else:
            self._instance_registry.wait()
        self._server.stop()
