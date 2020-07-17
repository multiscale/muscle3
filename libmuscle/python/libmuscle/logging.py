from enum import Enum
import logging
from typing import Dict

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp

from libmuscle.timestamp import Timestamp


class LogLevel(Enum):
    """Log levels for MUSCLE 3.

    These match the levels in the MUSCLE Manager Protocol, and should \
    be kept identical to those. They also match the Python logging log \
    levels, although not numerically.
    """
    CRITICAL = 5
    ERROR = 4
    WARNING = 3
    INFO = 1
    DEBUG = 0

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
                LogLevel.DEBUG: logging.DEBUG}
        return to_python_level[self]

    @staticmethod
    def from_grpc(
            level: mmp.LogLevel
            ) -> 'LogLevel':
        """Creates a log level from a gRPC-generated LogLevel message.

        Args:
            level: A log level, received from gRPC.

        Returns:
            The same log level, as a LogLevel.
        """
        log_level_map = {
                mmp.LOG_LEVEL_DEBUG: LogLevel.DEBUG,
                mmp.LOG_LEVEL_INFO: LogLevel.INFO,
                mmp.LOG_LEVEL_WARNING: LogLevel.WARNING,
                mmp.LOG_LEVEL_ERROR: LogLevel.ERROR,
                mmp.LOG_LEVEL_CRITICAL: LogLevel.CRITICAL
                }  # type: Dict[mmp.LogLevel, LogLevel]
        return log_level_map[level]

    def to_grpc(self) -> mmp.LogLevel:
        """Converts the log level to the gRPC generated type.

        Args:
            level: A log level.

        Returns:
            The same log level, as the gRPC type.
        """
        log_level_map = {
                LogLevel.DEBUG: mmp.LOG_LEVEL_DEBUG,
                LogLevel.INFO: mmp.LOG_LEVEL_INFO,
                LogLevel.WARNING: mmp.LOG_LEVEL_WARNING,
                LogLevel.ERROR: mmp.LOG_LEVEL_ERROR,
                LogLevel.CRITICAL: mmp.LOG_LEVEL_CRITICAL
                }  # type: Dict[LogLevel, mmp.LogLevel]
        return log_level_map[self]


class LogMessage:
    """A log message as used by MUSCLE 3.

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

    def to_grpc(self) -> mmp.LogMessage:
        """Converts the log message to the gRPC-generated type.

        Args:
            message: A log message.

        Returns:
            The same log message, as the gRPC type.
        """
        return mmp.LogMessage(
                instance_id=self.instance_id,
                timestamp=self.timestamp.to_grpc(),
                level=self.level.to_grpc(),
                text=self.text)
