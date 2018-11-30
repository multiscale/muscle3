from ymmsl import Reference

from libmuscle.mcp.message import Message


class Client:
    """A client that connects to an MCP server.

    This is a base class for MCP Clients. An MCP Client connects to
    an MCP Server over some lower-level communication protocol, and
    requests messages from it.
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

    def __init__(self, location: str) -> None:
        """Create an MCPClient for a given location.

        The client will connect to this location and be able to request
        messages from any compute element and port represented by it.

        Args:
            location: A location string.
        """
        self._location = location

    def receive(self, receiver: Reference) -> Message:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        raise NotImplementedError()     # pragma: no cover
