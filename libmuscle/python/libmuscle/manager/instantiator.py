import enum
import logging
import multiprocessing as mp
from pathlib import Path
from typing import Optional

from ymmsl import Implementation, Reference, ResourceRequirements

from libmuscle.planner.planner import Resources


class ProcessStatus(enum.Enum):
    """Status of a process (instance)."""
    STARTED = 0
    RUNNING = 1
    SUCCESS = 2
    ERROR = 3
    CANCELED = 4

    def is_finished(self) -> bool:
        """Returns whether the job is finished.

        Canceled jobs are considered finished, even if they've never
        run.
        """
        return self in (
                ProcessStatus.SUCCESS, ProcessStatus.ERROR,
                ProcessStatus.CANCELED)


class Process:
    """Represents a process.

    Attributes:
        instance: Name of instance this is the process of
        resources: The resources allocated to this process
        status: Current status of the process
        exit_code: Exit code, if status is ERROR
        error_msg: Error message, if status is ERROR
    """
    def __init__(self, instance: Reference, resources: Resources) -> None:
        """Create a Process object.

        Args:
            resources: Resources allocated to this process.
        """
        self.instance = instance
        self.resources = resources
        self.status = ProcessStatus.STARTED
        self.exit_code = None   # type: Optional[int]
        self.error_msg = None   # type: Optional[str]


class InstantiatorRequest:
    """Base class for requests to an instantiator."""
    pass


class ShutdownRequest(InstantiatorRequest):
    """Requests shutting down the background process.

    The process will stop once all running processes are done.
    """
    pass


class InstantiationRequest(InstantiatorRequest):
    """Requests instantiating a new process.

    Attributes:
        instance: The name of the instance
        implementation: The implementation to start for it
        resources: The resources to start it on
    """
    def __init__(
            self, instance: Reference, implementation: Implementation,
            res_req: ResourceRequirements, resources: Resources, instance_dir:
            Path, work_dir: Path, stdout_path: Path, stderr_path: Path
            ) -> None:
        """Create an InstantiationRequest.

        Args:
            instance: The name of the instance
            implementation: The implementation to start for it
            res_req: The resource requirements for this instance
            resources: The resources to instantiate on
            instance_dir: The main directory for this instance
            work_dir: The directory in which to start it
            stdout_path: Path of file to redirect stdout to
            stderr_path: Path of file to redirect stderr to
        """
        self.instance = instance
        self.implementation = implementation
        self.res_req = res_req
        self.resources = resources
        self.instance_dir = instance_dir
        self.work_dir = work_dir
        self.stdout_path = stdout_path
        self.stderr_path = stderr_path


class CancelAllRequest(InstantiatorRequest):
    """Requests stopping all running processes."""
    pass


class CrashedResult:
    """Signals that the instantiator process crashed."""
    pass


class QueueingLogHandler(logging.Handler):
    """A logging Handler that enqueues records."""
    def __init__(self, queue: mp.Queue) -> None:
        """Create a QueueingLogHandler.

        Args:
            level: The level of this handler
        """
        super().__init__()
        self._queue = queue

    def emit(self, record: logging.LogRecord) -> None:
        """Emit the record by enqueueing it.

        Args:
            record: A log record to enqueue.
        """
        self._queue.put(record)
