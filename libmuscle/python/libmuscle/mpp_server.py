from typing import List

import msgpack
from ymmsl import Reference

from libmuscle.mcp.protocol import RequestType
from libmuscle.mcp.transport_server import RequestHandler, TransportServer
from libmuscle.mcp.type_registry import transport_server_types
from libmuscle.post_office import PostOffice


class MPPRequestHandler(RequestHandler):
    """Handles peer protocol requests.

    This accepts peer protocol message requests and responds to them by
    getting messages from a PostOffice.
    """
    def __init__(self, post_office: PostOffice) -> None:
        """Create an MPPRequestHandler.

        Args:
            post_office: The PostOffice to get messages from.
        """
        self._post_office = post_office

    def handle_request(self, request: bytes) -> bytes:
        """Handle a request.

        This receives an MCP request and handles it by blocking until
        the requested message is available, then returning it.

        Args:
            request: A received request

        Returns:
            An encoded response
        """
        req = msgpack.unpackb(request, raw=False)
        if len(req) != 2 or req[0] != RequestType.GET_NEXT_MESSAGE.value:
            raise RuntimeError(
                    'Invalid request type. Did the streams get crossed?')
        recv_port = Reference(req[1])
        return self._post_office.get_message(recv_port)


class MPPServer:
    """Serves MPP requests.

    This manages a collection of servers for different protocols and a
    PostOffice that stores outgoing messages.
    """
    def __init__(self) -> None:
        self._post_office = PostOffice()
        self._handler = MPPRequestHandler(self._post_office)
        self._servers: List[TransportServer] = []

        for server_type in transport_server_types:
            server = server_type(self._handler)
            self._servers.append(server)

    def get_locations(self) -> List[str]:
        """Returns a list of locations that we can be reached at.

        These locations are of the form 'protocol:location', where
        the protocol name does not contain a colon and location may
        be an arbitrary string.

        Returns:
            A list of strings describing network locations.
        """
        return [server.get_location() for server in self._servers]

    def deposit(self, receiver: Reference, message: bytes) -> None:
        """Deposits a message for the receiver to retrieve.

        Args:
            receiver: Receiver of the message.
            message: The message to deposit.
        """
        self._post_office.deposit(receiver, message)

    def wait_for_receivers(self) -> None:
        """Waits for all deposited messages to have been received."""
        self._post_office.wait_for_receivers()

    def shutdown(self) -> None:
        """Shut down all servers."""
        for server in self._servers:
            server.close()
