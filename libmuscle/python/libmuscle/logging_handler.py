import logging

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import MMPClient


class MuscleManagerHandler(logging.Handler):
    """Standard Python log handler for the manager.

    A MuscleManagerHandler is a standard Python log handler, which can
    be attached to a logger, and forwards log messages to the Muscle
    Manager for central logging.
    """
    def __init__(self, instance_id: str, level: int, mmp_client: MMPClient
                 ) -> None:
        """Create a MuscleManagerHandler.

        Args:
            instance_id: The name of the instance we're logging for.
            level: The initial log level to use.
            mmp_client: The MMP Client to submit log messages to.
        """
        super().__init__(level)
        self._instance_id = instance_id
        self._manager = mmp_client

    def emit(self, record: logging.LogRecord) -> None:
        message = LogMessage(self._instance_id, Timestamp(record.created),
                             LogLevel.from_python_level(record.levelno),
                             record.message)
        self._manager.submit_log_message(message)
