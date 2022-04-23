import logging
from pathlib import Path
from typing import Optional

from libmuscle.logging import LogLevel, Timestamp
from libmuscle.util import extract_log_file_location


class Formatter(logging.Formatter):
    """A custom formatter that can format remote messages."""
    def usesTime(self) -> bool:
        """Tells the formatter to make asctime available."""
        return True

    def formatMessage(self, record: logging.LogRecord) -> str:
        """Formats a message for a record.

        If the record contains a time_stamp attribute, assumes that it
        is a remote record and formats accordingly, otherwise formats
        as a local record.

        Args:
            record: The LogRecord to format.

        Returns:
            The formatted message.
        """
        if 'instance' in record.__dict__:
            return (
                    '%(instance)-14s %(iasctime)-15s %(levelname)-7s'
                    ' %(name)s: %(message)s' % record.__dict__)
        return (
                'muscle_manager %(asctime)s %(levelname)-7s %(name)s:'
                ' %(message)s' % record.__dict__)


class Logger:
    """The MUSCLE 3 Manager Logger component.

    The Logger component takes log messages and writes them to
    standard out.

    Args:
        log_dir: Directory to write the log file into.
    """
    def __init__(self, log_dir: Optional[Path] = None) -> None:
        if log_dir is None:
            log_dir = Path.cwd()
        logfile = extract_log_file_location('muscle3_manager.log')
        if logfile is None:
            logfile = log_dir / 'muscle3_manager.log'
        self._local_handler = logging.FileHandler(str(logfile), mode='w')
        self._local_handler.setFormatter(Formatter())

        # Find and remove default handler to disable automatic console output
        # Testing for 'stderr' in the stringified version is not nice, but
        # seems reliable, and doesn't mess up pytest's caplog mechanism while
        # it also doesn't introduce a runtime dependency on pytest.
        logging.getLogger().handlers = [
                h for h in logging.getLogger().handlers
                if 'stderr' not in str(h)]

        # add our own
        logging.getLogger().addHandler(self._local_handler)

        # hardwired for now
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('qcg').setLevel(logging.WARNING)
        logging.getLogger('yatiml').setLevel(logging.WARNING)

    def close(self) -> None:
        logging.getLogger().removeHandler(self._local_handler)

    def log_message(
            self,
            instance_id: str,
            timestamp: Timestamp,
            level: LogLevel,
            text: str) -> None:
        """Log a message.

        Args:
            instance_id: Identifier of the instance that generated the \
                    message.
            timestamp: Time when this log message was generated, \
                    according to the clock on that machine.
            level: The log level of the message.
            text: The message text.
        """
        logger = logging.getLogger(instance_id)
        logger.log(
                level.as_python_level(),
                text,
                extra={
                    'instance': instance_id,
                    'iasctime': timestamp.to_asctime()})
