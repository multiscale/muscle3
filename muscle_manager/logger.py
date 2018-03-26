import logging

from libmuscle.logging import LogLevel, Timestamp
from libmuscle.operator import Operator


class Logger:
    """The MUSCLE 3 Manager Logger component.

    The Logger component takes log messages and writes them to
    standard out.
    """
    def __init__(self) -> None:
        logging.basicConfig(
                format='%(time_stamp)-15s: %(name)s ' +
                '(%(operator)s) %(levelname)s: %(message)s',
                level=logging.DEBUG)

    def log_message(
            self,
            instance_id: str,
            operator: Operator,
            timestamp: Timestamp,
            level: LogLevel,
            text: str) -> None:
        """Log a message.

        Args:
            instance_id: Identifier of the instance that generated the \
                    message.
            operator: The operator that generated the message.
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
                    'time_stamp': timestamp.to_rfc3339(),
                    'operator': operator.name})
