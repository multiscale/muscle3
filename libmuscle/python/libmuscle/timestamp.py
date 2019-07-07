import datetime

import google.protobuf.timestamp_pb2 as pbts


class Timestamp:
    """A timestamp, as the number of seconds since the UNIX epoch.

    Args:
        seconds: The number of seconds since the start of 1970.
    """
    def __init__(self, seconds: float) -> None:
        self.__seconds = seconds

    def to_rfc3339(self) -> str:
        """Converts a Timestamp to a datetime string.

        Returns:
            The timestamp as a string.
        """
        date_time = datetime.datetime.utcfromtimestamp(self.__seconds)
        return date_time.isoformat() + 'Z'

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
        seconds = int(self.__seconds)
        nanos = int((self.__seconds - seconds) * 10**9)
        return pbts.Timestamp(seconds=seconds, nanos=nanos)
