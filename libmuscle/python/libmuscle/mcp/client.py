from ymmsl import Reference


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

    @staticmethod
    def shutdown(instance_id: Reference) -> None:
        """Shut down and free any resources shared by all clients.

        This is an optional hook for communication subsystems that
        need it. If implemented, it must work correctly even if no
        clients have ever been instantiated.

        This will be called after all clients of this class have been
        closed.
        """
        pass

    def __init__(self, instance_id: Reference, location: str) -> None:
        """Create an MCPClient for a given location.

        The client will connect to this location and be able to request
        messages from any compute element and port represented by it.

        Args:
            instance_id: Id of our instance.
            location: A location string for the peer.
        """
        self._location = location

    def receive(self, receiver: Reference) -> bytes:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        raise NotImplementedError()     # pragma: no cover

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        raise NotImplementedError()     # pragma: no cover
