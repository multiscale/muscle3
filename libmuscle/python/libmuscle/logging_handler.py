import logging

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import ConnectionLockedError, MMPClient


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
        self._num_dropped = 0

    def emit(self, record: logging.LogRecord) -> None:
        """Do the actual send to the manager

        If this fails, then we drop the message, but we do keep track of how many
        messages were dropped and try to get that into the manager log, referring the
        user to the instance log.
        """
        message = LogMessage(self._instance_id, Timestamp(record.created),
                             LogLevel.from_python_level(record.levelno),
                             self.format(record))

        try:
            if self._num_dropped > 0:
                dropped_msg = LogMessage(
                        self._instance_id, Timestamp(), LogLevel.WARNING,
                        f'{self._num_dropped} log messages were not sent to the manager'
                        ' log due to manager overload or network connectivity problems.'
                        ' Please see the instance log to read them.')
                self._manager.submit_log_message(dropped_msg)
                self._num_dropped = 0

            self._manager.submit_log_message(message)

        except ConnectionLockedError:
            self._num_dropped += 1
