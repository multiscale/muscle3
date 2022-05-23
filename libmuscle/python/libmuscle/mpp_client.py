from typing import List, Optional

import msgpack
from ymmsl import Reference

from libmuscle.mcp.protocol import RequestType
from libmuscle.mcp.transport_client import TransportClient
from libmuscle.mcp.type_registry import transport_client_types


class MPPClient:
    """A client that connects to an MPP server.

    This client connects to a peer to retrieve messages. It uses an MCP
    Transport to connect.
    """
    def __init__(self, locations: List[str]) -> None:
        """Create an MPPClient for the given peer.

        The client will connect to the peer on one of its locations. It
        tries the most efficient protocol first. Once connected, it can
        request messages from any component and port represented by it.

        Args:
            locations: The peer's location strings
        """
        client = None       # type: Optional[TransportClient]
        for ClientType in transport_client_types:
            for location in locations:
                if ClientType.can_connect_to(location):
                    try:
                        client = ClientType(location)
                        break
                    except Exception:
                        pass
            if client:
                break
        else:
            raise RuntimeError('Failed to connect')

        self._transport_client = client

    def receive(self, receiver: Reference) -> bytes:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        request = [RequestType.GET_NEXT_MESSAGE.value, str(receiver)]
        encoded_request = msgpack.packb(request, use_bin_type=True)
        return self._transport_client.call(encoded_request)

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        self._transport_client.close()
