import datetime
import time
from typing import Optional


class Timestamp:
    """A timestamp, as the number of seconds since the UNIX epoch.

    Args:
        seconds: The number of seconds since the start of 1970.
    """
    def __init__(self, seconds: Optional[float] = None) -> None:
        """Create a Timestamp representing the given time, or now.

        If seconds is None, the current time is used.
        """
        if seconds is None:
            seconds = time.time()
        self.seconds = seconds

    def to_asctime(self) -> str:
        """Converts a Timestamp to a LogRecord asctime.

        Returns:
            The timestamp as a string in the format used by default
            by Python's logging subsystem.
        """
        date_time = datetime.datetime.fromtimestamp(self.seconds)
        whole_part = date_time.strftime('%Y-%m-%d %H:%M:%S')
        return '%s,%03d' % (whole_part, date_time.time().microsecond / 1000)
