from enum import Enum
import logging

from muscle_manager.operator import Operator


class LogLevel(Enum):
    CRITICAL = 5
    ERROR = 4
    WARNING = 3
    PROFILE = 2
    INFO = 1
    DEBUG = 0

    def as_python_level(self) -> int:
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

        self.__logger.log(
                level.as_python_level(),
                text,
                extra={
                    'time_stamp': time_stamp,
                    'instance_id': instance_id,
                    'operator': operator.name})
