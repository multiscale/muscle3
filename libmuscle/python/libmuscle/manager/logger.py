import logging

from libmuscle.logging import LogLevel, Timestamp
from libmuscle.operator import Operator
from libmuscle.util import extract_log_file_location


class Logger:
    """The MUSCLE 3 Manager Logger component.

    The Logger component takes log messages and writes them to
    standard out.
    """
    def __init__(self) -> None:
        logfile = extract_log_file_location('muscle3_manager.log')
        local_handler = logging.FileHandler(str(logfile), mode='w')
        formatter = logging.Formatter('%(time_stamp)-15s: %(name)s'
                                      ' %(levelname)s: %(message)s')
        local_handler.setFormatter(formatter)

        # Find and remove default handler to disable automatic console output
        # Testing for 'stderr' in the stringified version is not nice, but
        # seems reliable, and doesn't mess up pytest's caplog mechanism while
        # it also doesn't introduce a runtime dependency on pytest.
        logging.getLogger().handlers = [
                h for h in logging.getLogger().handlers
                if 'stderr' not in str(h)]

        # add our own
        logging.getLogger().addHandler(local_handler)

        # hardwired for now
        logging.getLogger().setLevel(logging.INFO)
        logging.getLogger('yatiml.loader').setLevel(logging.WARNING)
        logging.getLogger('yatiml.dumper').setLevel(logging.WARNING)

    def log_message(
            self,
            instance_id: str,
            timestamp: Timestamp,
            level: LogLevel,
            text: str) -> None:
        """Log a message.

        Args:
            instance_id: Identifier of the instance that generated the \
                    message.
            timestamp: Time when this log message was generated, \
                    according to the clock on that machine.
            level: The log level of the message.
            text: The message text.
        """
        logger = logging.getLogger(instance_id)
        logger.log(
                level.as_python_level(),
                text,
                extra={'time_stamp': timestamp.to_rfc3339()})
