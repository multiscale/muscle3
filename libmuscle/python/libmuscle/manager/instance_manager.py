import logging
from pathlib import Path
from textwrap import indent
from threading import Thread
from typing import Dict, List, Optional, Tuple, Union
from multiprocessing import Queue
from queue import Empty

from ymmsl import Configuration, Reference

from libmuscle.errors import ConfigurationError
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, InstantiatorRequest,
        InstantiationRequest, Process, ProcessStatus, ShutdownRequest)
from libmuscle.manager.logger import last_lines
from libmuscle.manager.run_dir import RunDir
from libmuscle.native_instantiator.native_instantiator import NativeInstantiator
from libmuscle.planner.planner import Planner, ResourceAssignment
from libmuscle.planner.resources import Resources


_logger = logging.getLogger(__name__)


class LogHandlingThread(Thread):
    """Pumps log records from a queue.

    This gets log records from a queue and sends them to the logging
    system.
    """
    def __init__(self, queue: Queue) -> None:
        """Creates a LogHandlingThread.

        Args:
            queue: Queue to get log records from.
        """
        super().__init__()
        self._queue = queue
        self._shutting_down = False

    def shutdown(self) -> None:
        """Process remaining records and stop the thread."""
        self._shutting_down = True

    def run(self) -> None:
        """The thread's entry point."""
        while True:
            try:
                record = self._queue.get(True, 0.1)
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except Empty:
                if self._shutting_down:
                    break


_ResultType = Union[Process, CrashedResult]


class InstanceManager:
    """Instantiates and manages running instances"""
    def __init__(
            self, configuration: Configuration, run_dir: RunDir,
            instance_registry: InstanceRegistry) -> None:
        """Create an InstanceManager.

        Args:
            configuration: The global configuration
            run_dir: Directory to run in
            instance_registry: The InstanceRegistry to use
        """
        self._configuration = configuration
        self._run_dir = run_dir
        self._instance_registry = instance_registry

        self._resources_in: Queue[Resources] = Queue()
        self._requests_out: Queue[InstantiatorRequest] = Queue()
        self._results_in: Queue[_ResultType] = Queue()
        self._log_records_in: Queue[logging.LogRecord] = Queue()

        self._instantiator = NativeInstantiator(
                self._resources_in, self._requests_out, self._results_in,
                self._log_records_in, self._run_dir.path)
        self._instantiator.start()

        self._log_handler = LogHandlingThread(self._log_records_in)
        self._log_handler.start()

        self._allocations: Optional[Dict[Reference, ResourceAssignment]] = None

        resources = self._resources_in.get()
        _logger.debug(f'Got resources {resources}')
        if isinstance(resources, CrashedResult):
            msg = (
                'Instantiator crashed. This should not happen, please file a bug'
                ' report.')
            _logger.error(msg)
            raise RuntimeError(msg) from resources.exception

        self._planner = Planner(resources)
        self._num_running = 0

    def set_manager_location(self, location: str) -> None:
        """Sets the network location of the manager.

        Call this before starting any instances so that the location
        can be passed to them.

        Args:
            location: The network location (e.g. localhost:5000)
        """
        self._manager_location = location

    def start_all(self) -> None:
        """Starts all the instances of the model."""
        self._allocations = self._planner.allocate_all(self._configuration)
        for instance, resources in self._allocations.items():
            _logger.info(f'Planned {instance} on {resources.as_resources()}')

        components = {c.name: c for c in self._configuration.model.components}
        for instance, resources in self._allocations.items():
            component = components[instance.without_trailing_ints()]
            if component.implementation is None:
                _logger.warning(
                        f'No implementation specified for {component.name}'
                        ', not starting it.')
                continue
            implementation = self._configuration.implementations[
                    component.implementation]
            implementation.env['MUSCLE_MANAGER'] = self._manager_location
            idir = self._run_dir.add_instance_dir(instance)
            workdir = idir / 'workdir'
            workdir.mkdir()
            stdout_path = idir / 'stdout.txt'
            stderr_path = idir / 'stderr.txt'

            request = InstantiationRequest(
                    instance, implementation,
                    self._configuration.resources[component.name],
                    resources, idir, workdir, stdout_path, stderr_path)
            _logger.info(f'Instantiating {instance}')
            self._requests_out.put(request)
            self._num_running += 1

    def get_resources(self) -> Dict[Reference, ResourceAssignment]:
        """Returns the resources allocated to each instance.

        Only call this after start_all() has been called, or it will raise
        an exception because the information is not available.

        Return:
            The resources for each instance instantiated by start_all()
        """
        if self._allocations is None:
            raise RuntimeError(
                    'Tried to get resources but we are running without --start-all')

        return self._allocations

    def wait(self) -> bool:
        """Waits for all instances to be done."""
        all_seemingly_okay = True

        def cancel_all() -> None:
            nonlocal all_seemingly_okay
            if all_seemingly_okay:
                self._requests_out.put(CancelAllRequest())
                all_seemingly_okay = False

        # Get all results
        results: List[Process] = list()

        while self._num_running > 0:
            result = self._results_in.get()

            if isinstance(result, CrashedResult):
                if isinstance(result.exception, ConfigurationError):
                    _logger.error(str(result.exception))
                else:
                    _logger.error(
                        'Instantiator crashed. This should not happen, please file'
                        ' a bug report.')
                return False

            results.append(result)
            if result.status != ProcessStatus.CANCELED:
                registered = self._instance_registry.did_register(result.instance)
                if result.exit_code != 0 or not registered:
                    cancel_all()
            self._num_running -= 1

        # Summarise outcome
        crashes: List[Tuple[Process, Path]] = list()
        indirect_crashes: List[Tuple[Process, Path]] = list()

        for result in results:
            if result.status == ProcessStatus.CANCELED:
                if result.exit_code == 0:
                    _logger.info(
                            f'Instance {result.instance} was not started'
                            f' because of an error elsewhere')
                else:
                    _logger.info(
                            f'Instance {result.instance} was shut down by'
                            f' MUSCLE3 because an error occurred elsewhere')
                # Ensure we don't see this as a succesful run when shutdown() is called
                # by another thread:
                all_seemingly_okay = False
            else:
                stderr_file = (
                        self._run_dir.instance_dir(result.instance) /
                        'stderr.txt')
                if result.exit_code == 0:
                    if self._instance_registry.did_register(result.instance):
                        _logger.info(
                                f'Instance {result.instance} finished with'
                                ' exit code 0')
                    else:
                        _logger.error(
                                f'Instance {result.instance} quit with no error'
                                ' (exit code 0), but it never registered with the'
                                ' manager. Maybe it never created an Instance'
                                ' object?')
                        crashes.append((result, stderr_file))
                else:
                    try:
                        with stderr_file.open() as f:
                            peer_crash = any(['peer crash?' in line for line in f])
                    except FileNotFoundError:
                        peer_crash = False

                    if peer_crash:
                        _logger.warning(
                                f'Instance {result.instance} crashed, likely because'
                                f' an error occurred elsewhere.')
                        indirect_crashes.append((result, stderr_file))
                    else:
                        _logger.error(
                                f'Instance {result.instance} quit with exit code'
                                f' {result.exit_code}')
                        crashes.append((result, stderr_file))

            _logger.debug(f'Status: {result.status}')
            _logger.debug(f'Exit code: {result.exit_code}')
            _logger.debug(f'Error msg: {result.error_msg}')

        # Show errors from crashed components
        if crashes:
            for result, stderr_file in crashes:
                _logger.error(
                        f'The last error output of {result.instance} was:')
                _logger.error(
                        '\n' + indent(last_lines(stderr_file, 20), '    '))
                _logger.error(
                        'More output may be found in'
                        f' {self._run_dir.instance_dir(result.instance)}\n'
                        )
        elif indirect_crashes:
            # Possibly a component exited without error, but prematurely. If this
            # caused ancillary crashes due to dropped connections, then the logs
            # of those will give a hint as to what the problem may be, so print
            # those instead.
            _logger.error(
                    'At this point, one or more instances crashed because they'
                    ' lost their connection to another instance, but no other'
                    ' crashing instance was found that could have caused this.')
            _logger.error(
                    'This means that either another instance quit before it was'
                    ' supposed to, but with exit code 0, or there was an actual'
                    ' network problem that caused the connection to drop.')
            _logger.error(
                    'Here is the output of the instances that lost connection:')
            for result, stderr_file in indirect_crashes:
                _logger.error(
                        f'The last error output of {result.instance} was:')
                _logger.error(
                        '\n' + indent(last_lines(stderr_file, 20), '    '))
                _logger.error(
                        'More output may be found in'
                        f' {self._run_dir.instance_dir(result.instance)}\n'
                        )
        elif not all_seemingly_okay:
            # shutdown() was called by another thread (e.g. the DeadlockDetector):
            _logger.error('The simulation was aborted.')
        else:
            _logger.info('The simulation finished without error.')

        return all_seemingly_okay

    def shutdown(self) -> None:
        """Shuts down the backend.

        This will wait for any processes still running before shutting
        down and returning.
        """
        _logger.debug('Shutting down instance manager')
        self._requests_out.put(CancelAllRequest())
        self._requests_out.put(ShutdownRequest())
        self._instantiator.join()
        self._log_handler.shutdown()
        self._log_handler.join()
        # Close multiprocessing.Queues and ensure their feeder threads exit
        queues: List[Queue] = [
                self._resources_in, self._requests_out,
                self._results_in, self._log_records_in]
        for queue in queues:
            queue.close()
            queue.join_thread()
        _logger.debug('Instance manager shut down cleanly')
