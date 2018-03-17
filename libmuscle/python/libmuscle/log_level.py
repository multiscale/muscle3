from enum import Enum
import logging


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
