from ymmsl import Reference

from libmuscle.post_office import PostOffice


class ServerNotSupported(RuntimeError):
    pass


class Server:
    """A server that accepts MCP connections.

    This is a base class for MCP Servers. An MCP Server accepts
    connections over some lower-level communication protocol, and
    processes message requests by sending the requested message.
    """
    def __init__(self, instance_id: Reference, post_office: PostOffice
                 ) -> None:
        """Create a Server.

        Args:
            instance_id: Id of the instance we're a server for.
            post_office: A PostOffice to obtain data from.
        """
        self._instance_id = instance_id
        self._post_office = post_office

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        raise NotImplementedError()  # pragma: no cover

    def close(self) -> None:
        """Closes this server.

        Stops the server listening, waits for existing clients to
        disconnect, then frees any other resources.
        """
        raise NotImplementedError()  # pragma: no cover
