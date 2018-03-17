from enum import Enum
import logging

from muscle_manager.operator import Operator


class LogLevel(Enum):
    """Log levels for MUSCLE 3.

    These match the levels in the MUSCLE Manager Protocol, and should \
    be kept identical to those. They also match the Python logging log \
    levels, with an additional PROFILE level. This is to be used by \
    libmuscle for messages intended for the built-in simple profiling \
    algorithm.
    """
    CRITICAL = 5
    ERROR = 4
    WARNING = 3
    PROFILE = 2
    INFO = 1
    DEBUG = 0

    def as_python_level(self) -> int:
        """Convert the LogLevel to the corresponding Python level."""
        to_python_level = {
                LogLevel.CRITICAL: logging.CRITICAL,
                LogLevel.ERROR: logging.ERROR,
                LogLevel.WARNING: logging.WARNING,
                LogLevel.PROFILE: logging.INFO,
                LogLevel.INFO: logging.INFO,
                LogLevel.DEBUG: logging.DEBUG}

        return to_python_level[self]


class Logger:
    """The MUSCLE 3 Manager Logger component.

    The Logger component takes log messages and writes them to
    standard out.
    """
    def __init__(self) -> None:
        logging.basicConfig(
                format='%(time_stamp)-15s: %(instance_id)s ' +
                '(%(operator)s) %(levelname)s: %(message)s')
        self.__logger = logging.getLogger("muscle3.manager")

    def log_message(
            self,
            instance_id: str,
            operator: Operator,
            time_stamp: str,
            level: LogLevel,
            text: str) -> None:
        """Log a message.

        Args:
            instance_id: Identifier of the instance that generated the \
                    message.
            operator: The operator that generated the message.
            time_stamp: Time when this log message was generated, \
                    according to the clock on that machine.
            level: The log level of the message.
            text: The message text.
        """
        self.__logger.log(
                level.as_python_level(),
                text,
                extra={
                    'time_stamp': time_stamp,
                    'instance_id': instance_id,
                    'operator': operator.name})
