class RequestHandler:
    """Handles requests sent to a TransportServer.

    TransportServers operate in terms of chunks of bytes received and
    sent in return. RequestHandlers interpret received chunks of bytes,
    handle the request, and return a chunk of bytes containing an
    encoded response.
    """
    def handle_request(self, request: bytes) -> bytes:
        """Handle a request.

        Args:
            request: A received request

        Returns:
            An encoded response
        """
        raise NotImplementedError()     # pragma: no cover


class ServerNotSupported(RuntimeError):
    pass


class TransportServer:
    """A server that accepts MCP connections.

    This is a base class for MCP Servers. An MCP Server accepts
    connections over some lower-level communication protocol, receives
    requests and returns responses from a RequestHandler.
    """
    def __init__(self, handler: RequestHandler) -> None:
        """Create a TransportServer.

        Args:
            handler: A handler to handle requests.
        """
        self._handler = handler

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
