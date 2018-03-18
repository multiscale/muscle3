from enum import Enum
import logging
from typing import Dict, NewType

import muscle_manager.protocol.muscle_manager_protocol_pb2 as mmp
import google.protobuf.timestamp_pb2 as pbts

from libmuscle.operator import Operator


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
                mmp.LOG_LEVEL_PROFILE: LogLevel.PROFILE,
                mmp.LOG_LEVEL_WARNING: LogLevel.WARNING,
                mmp.LOG_LEVEL_ERROR: LogLevel.ERROR,
                mmp.LOG_LEVEL_CRITICAL: LogLevel.CRITICAL
                }  # type: Dict[int, LogLevel]
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
                LogLevel.PROFILE: mmp.LOG_LEVEL_PROFILE,
                LogLevel.WARNING: mmp.LOG_LEVEL_WARNING,
                LogLevel.ERROR: mmp.LOG_LEVEL_ERROR,
                LogLevel.CRITICAL: mmp.LOG_LEVEL_CRITICAL
                }  # type: Dict[LogLevel, int]
        return log_level_map[self]


Timestamp = NewType('Timestamp', float)
"""A timestamp, as the number of seconds since the UNIX epoch."""


def timestamp_to_grpc(
        timestamp: Timestamp
        ) -> pbts.Timestamp:
    """Converts a Timestamp to the gRPC type.

    Args:
        timestamp: A timestamp.

    Returns:
        The same timestamp, as a gRPC object.
    """
    seconds = int(timestamp)
    nanos = int((timestamp - seconds) * 10**9)
    return pbts.Timestamp(seconds=seconds, nanos=nanos)


class LogMessage:
    """A log message as used by MUSCLE 3.

    Args:
        instance_id: The identifier of the instance that generated \
                this message.
        operator: The kernel operator that generated this message.
        timestamp: When the message was generated.
        level: Log level of the message.
        text: Contents of the message.

    Attributes:
        instance_id: The identifier of the instance that generated \
                this message.
        operator: The kernel operator that generated this message.
        timestamp: When the message was generated.
        level: Log level of the message.
        text: Contents of the message.
    """
    def __init__(
            self,
            instance_id: str,
            operator: Operator,
            timestamp: Timestamp,
            level: LogLevel,
            text: str
            ) -> None:

        self.instance_id = instance_id
        self.operator = operator
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
                operator=self.operator.to_grpc(),
                timestamp=timestamp_to_grpc(self.timestamp),
                level=self.level.to_grpc(),
                text=self.text)
