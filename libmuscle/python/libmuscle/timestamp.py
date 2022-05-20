import datetime


class Timestamp:
    """A timestamp, as the number of seconds since the UNIX epoch.

    Args:
        seconds: The number of seconds since the start of 1970.
    """
    def __init__(self, seconds: float) -> None:
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
