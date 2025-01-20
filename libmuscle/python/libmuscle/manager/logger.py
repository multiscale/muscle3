import logging
from pathlib import Path
from typing import List, Optional

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
    """The MUSCLE3 Manager Logger component.

    The Logger component configures the local logging system to output
    to the central log file, and it accepts messages from remote
    instances to write to it as well. Log levels are also set here.

    """
    def __init__(
            self, log_dir: Optional[Path] = None,
            log_level: Optional[str] = None) -> None:
        """Create a Logger.

        Log levels may be any of the Python predefined log levels, i.e.
        critical, error, warning, info and debug, and they're
        case_insensitive.

        Args:
            log_dir: Directory to write the log file into.
            log_level: Log level to set.
        """

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

        # set the root logger to log everything, so remote messages
        # are always logged
        logging.getLogger().setLevel(logging.NOTSET)

        # set Manager log level
        if log_level is None:
            log_level = 'INFO'
        else:
            log_level = log_level.upper()

        logging.getLogger('libmuscle').setLevel(log_level)

        # YAtiML should be pretty reliable, and if there is an issue
        # then we can easily load the problem file in Python by hand
        # using the yMMSL library and set the log level there.
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


def last_lines(file: Path, count: int) -> str:
    """Utility function that returns the last lines of a text file.

    This opens the file and returns the final `count` lines. It reads
    at most 10000 bytes, to avoid memory problems if the file contains
    e.g. a large amount of binary data.

    Args:
        file: The file to read
        count: Number of lines to read

    Return:
        A string of at most 10000 bytes, containing at most `count`
        newlines.
    """
    if not file.exists():
        return ''

    file_size = file.stat().st_size
    start_point = max(file_size - 10000, 0)

    lines: List[str] = []
    with file.open('r') as f:
        f.seek(start_point)
        f.readline()    # skip partial line
        line = f.readline()
        while line:
            lines.append(line)
            line = f.readline()

    return '\n' + ''.join(lines[-count:])
