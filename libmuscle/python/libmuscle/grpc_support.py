from libmuscle.log_level import LogLevel
from libmuscle.operator import Operator
import muscle_manager.protocol.muscle_manager_protocol_pb2 as mmp

from typing import Dict


def operator_from_grpc(
        operator: mmp.Operator
        ) -> Operator:
    """Converts an operator from the gRPC-generated Operator type to \
            the Manager's native Python type.

    Args:
        operator: An operator, received from gRPC.

    Returns:
        The same operator, as the internal type.
    """
    operator_map = {
            mmp.OPERATOR_NONE: Operator.NONE,
            mmp.OPERATOR_F_INIT: Operator.F_INIT,
            mmp.OPERATOR_O_I: Operator.O_I,
            mmp.OPERATOR_S: Operator.S,
            mmp.OPERATOR_B: Operator.B,
            mmp.OPERATOR_O_F: Operator.O_F,
            mmp.OPERATOR_MAP: Operator.MAP
            }   # type: Dict[int, Operator]
    return operator_map[operator]


def log_level_from_grpc(
        level: mmp.LogLevel
        ) -> LogLevel:
    """Converts a log level from the gRPC-generated LogLevel type to \
            the Manager's native Python type.

    Args:
        level: A log level, received from gRPC.

    Returns:
        The same log level, as the internal type.
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
