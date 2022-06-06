import logging
from threading import Thread
from typing import Union
from multiprocessing import Queue
import queue

from ymmsl import Configuration

from libmuscle.manager.instantiator import (
        CancelAllRequest, CrashedResult, InstantiatorRequest,
        InstantiationRequest, ProcessStatus, ShutdownRequest)
from libmuscle.manager.qcgpj_instantiator import Process, QCGPJInstantiator
from libmuscle.manager.run_dir import RunDir
from libmuscle.planner.planner import Planner, Resources


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
                record = self._queue.get(True, 1.0)
                logger = logging.getLogger(record.name)
                logger.handle(record)
            except queue.Empty:
                if self._shutting_down:
                    break


_ResultType = Union[Process, CrashedResult]


class InstanceManager:
    """Instantiates and manages running instances"""
    def __init__(
            self, configuration: Configuration, run_dir: RunDir) -> None:
        """Create a ProcessManager.

        Args:
            configuration: The global configuration
            run_dir: Directory to run in
        """
        self._configuration = configuration
        self._run_dir = run_dir

        self._resources_in = Queue()    # type: Queue[Resources]
        self._requests_out = Queue()    # type: Queue[InstantiatorRequest]
        self._results_in = Queue()      # type: Queue[_ResultType]
        self._log_records_in = Queue()  # type: Queue[logging.LogRecord]

        self._instantiator = QCGPJInstantiator(
                self._resources_in, self._requests_out, self._results_in,
                self._log_records_in, self._run_dir.path)
        self._instantiator.start()

        self._log_handler = LogHandlingThread(self._log_records_in)
        self._log_handler.start()

        self._planner = Planner(self._resources_in.get())
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
        allocations = self._planner.allocate_all(self._configuration)
        for instance, resources in allocations.items():
            _logger.info(f'Planned {instance} on {resources}')

        components = {c.name: c for c in self._configuration.model.components}
        for instance, resources in allocations.items():
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
            _logger.info(f'Instantiating {instance} on {resources}')
            self._requests_out.put(request)
            self._num_running += 1

    def wait(self) -> bool:
        """Waits for all instances to be done."""
        all_seemingly_okay = True
        while self._num_running > 0:
            result = self._results_in.get()

            if isinstance(result, CrashedResult):
                _logger.error(
                    'Instantiator crashed. This should not happen, please file'
                    ' a bug report.')
                return False

            if result.exit_code != 0:
                if result.status == ProcessStatus.CANCELED:
                    _logger.info(
                            f'Instance {result.instance} was shut down by'
                            f' MUSCLE3 because an error occurred elsewhere')
                else:
                    _logger.error(
                            f'Instance {result.instance} quit with error'
                            f' {result.exit_code}')
                    _logger.error(
                            'Output may be found in'
                            f' {self._run_dir.instance_dir(result.instance)}')
                    if all_seemingly_okay:
                        self._requests_out.put(CancelAllRequest())
                        all_seemingly_okay = False
            else:
                if result.status == ProcessStatus.CANCELED:
                    _logger.info(
                            f'Instance {result.instance} was not started'
                            f' because of an error elsewhere')
                else:
                    _logger.debug(f'Instance {result.instance} finished')
                    _logger.debug(f'States: {result.status}')
                    _logger.debug(f'Exit code: {result.exit_code}')
                    _logger.debug(f'Error msg: {result.error_msg}')

            self._num_running -= 1
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
        _logger.debug('Instance manager shut down cleanly')
