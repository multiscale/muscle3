from pathlib import Path
import logging
import sys
import traceback
from typing import Optional

from ymmsl import PartialConfiguration, save as save_ymmsl

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.instance_manager import InstanceManager
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.topology_store import TopologyStore


_logger = logging.getLogger(__name__)


class Manager:
    """The MUSCLE3 manager.

    This creates and manages instances and connects them together
    according to the simulation configuration.
    """
    def __init__(
            self, configuration: PartialConfiguration,
            run_dir: Optional[RunDir] = None, log_level: Optional[str] = None
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
        log_dir = self._run_dir.path if self._run_dir else Path.cwd()
        self._logger = Logger(log_dir, log_level)
        self._topology_store = TopologyStore(configuration)
        self._instance_registry = InstanceRegistry()

        if self._run_dir:
            save_ymmsl(
                    self._configuration,
                    self._run_dir.path / 'configuration.ymmsl')

        self._instance_manager = None    # type: Optional[InstanceManager]
        try:
            configuration = self._configuration.as_configuration()
            if self._run_dir is not None:
                self._instance_manager = InstanceManager(
                        configuration, self._run_dir)
        except ValueError:
            pass

        self._server = MMPServer(
                self._logger, self._configuration.settings,
                self._instance_registry, self._topology_store)

        if self._instance_manager:
            self._instance_manager.set_manager_location(
                    self.get_server_location())

    def get_server_location(self) -> str:
        """Returns the network location of the server."""
        return self._server.get_location()

    def start_instances(self) -> None:
        """Starts all required component instances."""
        if self._run_dir is None:
            raise RuntimeError('No run dir specified')
        if not self._instance_manager:
            raise RuntimeError(
                    'For MUSCLE3 to be able to start instances, the'
                    ' configuration must contain a model, implementations,'
                    ' and resources. Please make sure they are all there.')
        try:
            self._instance_manager.start_all()
        except:     # noqa
            _logger.error('An error occurred while starting the components:')
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)
            self._instance_manager.shutdown()
            raise

    def stop(self) -> None:
        """Shuts down the manager."""
        # self._server.stop()
        self._server.stop()
        self._logger.close()

    def wait(self) -> bool:
        """Blocks until the simulation is done, then shuts down.

        Returns:
            True if success, False if an error occurred.
        """
        if self._instance_manager:
            try:
                success = self._instance_manager.wait()
            finally:
                self._instance_manager.shutdown()
        else:
            self._instance_registry.wait()
            success = True
        self.stop()
        return success
