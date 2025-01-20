from pathlib import Path
import logging
import sys
import traceback
from typing import Optional

from ymmsl import Model, PartialConfiguration, save as save_ymmsl

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.instance_manager import InstanceManager
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.snapshot_registry import SnapshotRegistry
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.manager.deadlock_detector import DeadlockDetector


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
        self._profile_store = ProfileStore(log_dir)
        self._topology_store = TopologyStore(configuration)
        self._instance_registry = InstanceRegistry()
        self._deadlock_detector = DeadlockDetector()
        if run_dir is not None:
            snapshot_dir = run_dir.snapshot_dir()
        else:
            snapshot_dir = Path.cwd()
            if self._configuration.checkpoints:
                _logger.warning('Checkpoints are configured but no run'
                                ' directory is provided. Snapshots will be'
                                ' stored in the current working directory.')

        if self._run_dir:
            save_ymmsl(
                    self._configuration,
                    self._run_dir.path / 'configuration.ymmsl')

        if isinstance(self._configuration.model, Model):
            self._profile_store.store_instances([
                instance_name
                for c in self._configuration.model.components
                for instance_name in c.instances()])

        self._instance_manager: Optional[InstanceManager] = None
        try:
            configuration = self._configuration.as_configuration()
            if self._run_dir is not None:
                self._instance_manager = InstanceManager(
                        configuration, self._run_dir, self._instance_registry)
        except ValueError:
            pass

        # SnapshotRegistry creates a worker thread, must be created after
        # instance_manager which forks the process
        self._snapshot_registry = SnapshotRegistry(
                configuration, snapshot_dir, self._topology_store)
        self._snapshot_registry.start()

        self._server = MMPServer(
                self._logger, self._profile_store, self._configuration,
                self._instance_registry, self._topology_store,
                self._snapshot_registry, self._deadlock_detector, run_dir)

        if self._instance_manager:
            self._instance_manager.set_manager_location(
                    self.get_server_location())

    def get_server_location(self) -> str:
        """Returns the network location of the server."""
        return self._server.get_location()

    def start_instances(self) -> None:
        """Starts all required component instances."""
        if self._run_dir is None:
            message = 'No run dir specified'
            _logger.error(message)
            raise RuntimeError(message)
        if not self._instance_manager:
            message = (
                    'For MUSCLE3 to be able to start instances, the'
                    ' configuration must contain a model, implementations,'
                    ' and resources. Please make sure they are all there.')
            _logger.error(message)
            raise RuntimeError(message)
        try:
            self._instance_manager.start_all()
            self._profile_store.store_resources(
                    self._instance_manager.get_resources())
        except:     # noqa
            _logger.error('An error occurred while starting the components:')
            for line in traceback.format_exception(*sys.exc_info()):
                _logger.error(line)
            self._instance_manager.shutdown()
            raise

    def stop(self) -> None:
        """Shuts down the manager."""
        if self._instance_manager:
            self._instance_manager.shutdown()
        self._server.stop()
        self._snapshot_registry.shutdown()
        self._snapshot_registry.join()
        self._profile_store.shutdown()
        self._logger.close()

    def wait(self) -> bool:
        """Blocks until the simulation is done, then shuts down.

        Returns:
            True if success, False if an error occurred.
        """
        try:
            if self._instance_manager:
                success = self._instance_manager.wait()
            else:
                self._instance_registry.wait()
                success = True
        finally:
            self.stop()
        return success
