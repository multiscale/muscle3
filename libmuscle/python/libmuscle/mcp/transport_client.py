from typing import Tuple

from libmuscle.profiling import ProfileTimestamp


ProfileData = Tuple[ProfileTimestamp, ProfileTimestamp, ProfileTimestamp]


class TransportClient:
    """A client that connects to an MCP server.

    This is a base class for MCP Transport Clients. An MCP Transport
    Client connects to an MCP Transport Server over some communication
    protocol, requests messages from it, and returns responses.
    """
    @staticmethod
    def can_connect_to(location: str) -> bool:
        """Whether this client class can connect to the given location.

        Args:
            location: The location to potentially connect to.

        Returns:
            True iff this class can connect to this location.
        """
        raise NotImplementedError()     # pragma: no cover

    def call(self, request: bytes) -> Tuple[bytes, ProfileData]:
        """Send a request to the server and receive the response.

        This is a blocking call. Besides the result, this function
        returns a tuple with three timestamps (floats in seconds since
        the epoch). These were taken when the function was first called,
        when data became available and the transfer started, and when
        the transfer stopped.

        Args:
            request: The request to send

        Returns:
            The received response, and the timestamps
        """
        raise NotImplementedError()     # pragma: no cover

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities as needed.
        """
        raise NotImplementedError()     # pragma: no cover
