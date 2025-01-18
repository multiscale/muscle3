import enum
import logging
import multiprocessing as mp
import os
from pathlib import Path
import traceback
from typing import Dict, Optional

from ymmsl import BaseEnv, Implementation, Reference, ResourceRequirements

from libmuscle.planner.planner import ResourceAssignment


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
    def __init__(self, instance: Reference, resources: ResourceAssignment) -> None:
        """Create a Process object.

        Args:
            resources: Resources allocated to this process.
        """
        self.instance = instance
        self.resources = resources
        self.status = ProcessStatus.STARTED
        self.exit_code: Optional[int] = None
        self.error_msg: Optional[str] = None


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
        res_req: The resource requirements for this instance
        resources: The specific resources to start it on
        instance_dir: The main directory for this instance
        work_dir: The directory in which to start it
        stdout_path: Path of file to redirect stdout to
        stderr_path: Path of file to redirect stderr to
    """
    def __init__(
            self, instance: Reference, implementation: Implementation,
            res_req: ResourceRequirements, resources: ResourceAssignment,
            instance_dir: Path, work_dir: Path, stdout_path: Path, stderr_path: Path
            ) -> None:
        """Create an InstantiationRequest.

        Args:
            instance: The name of the instance
            implementation: The implementation to start for it
            res_req: The resource requirements for this instance
            resources: The specific resources to instantiate on
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
    def __init__(self, exception: Optional[BaseException] = None) -> None:
        self.exception = exception


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
        if record.exc_info:
            record.msg += '\n' + ''.join(
                    traceback.format_exception(*record.exc_info))
            record.exc_info = None

        self._queue.put(record)


def reconfigure_logging(queue: mp.Queue) -> None:
    """Reconfigure logging to send to queue.

    This reconfigures the logging subsystem to intercept all log
    messages and send them to the given queue, rather than to the
    previously configured handler.
    """
    root_logger = logging.getLogger()
    for h in list(root_logger.handlers):
        root_logger.removeHandler(h)

    handler = QueueingLogHandler(queue)
    root_logger.addHandler(handler)


def create_instance_env(
        instance: Reference, base_env: BaseEnv, overlay: Dict[str, str]
        ) -> Dict[str, str]:
    """Creates an environment for an instance.

    This takes the current (manager) environment variables and makes
    a copy, then adds or extends it according to the overlay given.

    Keys from overlay that start with + will have the corresponding
    value appended to the matching (by key, without the +) value in
    env, otherwise the value in env gets overwritten.
    """
    if base_env == BaseEnv.LOGIN:
        env = dict()
        for var in ('HOME', 'LOGNAME', 'SHELL', 'TERM', 'USER'):
            if var in os.environ:
                env[var] = os.environ[var]
    else:
        env = os.environ.copy()
        if base_env == BaseEnv.CLEAN:
            # Remove any virtual environment
            #
            # The deactivate command does not get exported by the activate script, so it
            # isn't available to us, as are most of the environment variables it uses to
            # deactivate the venv. So this is a bit of a hack, but it's the best we can
            # do. Note that _OLD_VIRTUAL_PYTHONHOME isn't exported by default either,
            # but we check for it anyway; if we're on a system where PYTHONHOME is
            # needed and the manager needs to be run with an active virtualenv and one
            # of the implementations needs a clean shell, then the user will have to
            # export it manually between activating the virtualenv and starting the
            # manager and things will work.
            vep = env.get('VIRTUAL_ENV_PROMPT')
            if vep is not None:
                if 'PS1' in env:
                    if env['PS1'].startswith(vep):
                        env['PS1'] = env['PS1'][len(vep):]
                del env['VIRTUAL_ENV_PROMPT']

            ovp = env.get('_OLD_VIRTUAL_PYTHONHOME')
            if ovp is not None:
                env['PYTHONHOME'] = ovp
                del env['_OLD_VIRTUAL_PYTHONHOME']

            venv = env.get('VIRTUAL_ENV')
            if venv is not None:
                path = env.get('PATH')
                if path is not None:
                    paths = [p for p in path.split(':') if p != venv + '/bin']
                    env['PATH'] = ':'.join(paths)

                del env['VIRTUAL_ENV']

    env['MUSCLE_INSTANCE'] = str(instance)

    for key, value in overlay.items():
        if key.startswith('+'):
            if key[1:] in env:
                env[key[1:]] += value
            else:
                env[key[1:]] = value
        else:
            env[key] = value
    return env
