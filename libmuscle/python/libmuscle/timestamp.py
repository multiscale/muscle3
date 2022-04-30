import datetime

import google.protobuf.timestamp_pb2 as pbts


class Timestamp:
    """A timestamp, as the number of seconds since the UNIX epoch.

    Args:
        seconds: The number of seconds since the start of 1970.
    """
    def __init__(self, seconds: float) -> None:
        self._seconds = seconds

    def to_asctime(self) -> str:
        """Converts a Timestamp to a LogRecord asctime.

        Returns:
            The timestamp as a string in the format used by default
            by Python's logging subsystem.
        """
        date_time = datetime.datetime.fromtimestamp(self._seconds)
        whole_part = date_time.strftime('%Y-%m-%d %H:%M:%S')
        return '%s,%03d' % (whole_part, date_time.time().microsecond / 1000)

    @staticmethod
    def from_grpc(timestamp: pbts.Timestamp) -> 'Timestamp':
        """Creates a Timestamp from a gRPC Timestamp message.

        Args:
            timestamp: A gRPC Timestamp from a gRPC call.

        Returns:
            The same timestamp as a Timestamp object.
        """
        return Timestamp(timestamp.seconds + timestamp.nanos * 1e-9)

    def to_grpc(self) -> pbts.Timestamp:
        """Converts a Timestamp to the gRPC type.

        Returns:
            The same timestamp, as a gRPC object.
        """
        seconds = int(self._seconds)
        nanos = int((self._seconds - seconds) * 10**9)
        return pbts.Timestamp(seconds=seconds, nanos=nanos)
