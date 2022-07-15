from enum import Enum
import logging

from libmuscle.timestamp import Timestamp


class LogLevel(Enum):
    """Log levels for MUSCLE3.

    These match the levels in the MUSCLE Manager Protocol, and should
    be kept identical to those. They also match the Python logging log
    levels.
    """
    DISABLE = 100
    CRITICAL = 50
    ERROR = 40
    WARNING = 30
    INFO = 20
    DEBUG = 10
    LOCAL = 0

    @staticmethod
    def from_python_level(level: int) -> 'LogLevel':
        """Creates a LogLevel from a Python log level.

        Args:
            level: A standard Python log level, such as logging.WARNING.

        Returns:
            The same level, but as a LogLevel.
        """
        if level > 40:
            return LogLevel.CRITICAL
        elif level > 30:
            return LogLevel.ERROR
        elif level > 20:
            return LogLevel.WARNING
        elif level > 10:
            return LogLevel.INFO
        return LogLevel.DEBUG

    def as_python_level(self) -> int:
        """Convert the LogLevel to the corresponding Python level."""
        to_python_level = {
                LogLevel.CRITICAL: logging.CRITICAL,
                LogLevel.ERROR: logging.ERROR,
                LogLevel.WARNING: logging.WARNING,
                LogLevel.INFO: logging.INFO,
                LogLevel.DEBUG: logging.DEBUG,
                LogLevel.LOCAL: logging.DEBUG}
        return to_python_level[self]


class LogMessage:
    """A log message as used by MUSCLE3.

    Args:
        instance_id: The identifier of the instance that generated \
                this message.
        timestamp: When the message was generated (real-world, not \
                simulation).
        level: Log level of the message.
        text: Content of the message.

    Attributes:
        instance_id: The identifier of the instance that generated \
                this message.
        timestamp: When the message was generated (real-world, not \
                simulation).
        level: Log level of the message.
        text: Content of the message.
    """
    def __init__(
            self,
            instance_id: str,
            timestamp: Timestamp,
            level: LogLevel,
            text: str
            ) -> None:

        self.instance_id = instance_id
        self.timestamp = timestamp
        self.level = level
        self.text = text
