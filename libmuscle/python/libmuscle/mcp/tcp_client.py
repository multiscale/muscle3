import socket

import msgpack
from ymmsl import Reference

from libmuscle.mcp.client import Client
from libmuscle.mcp.message import Message


class TcpClient(Client):
    """A client that connects to an MCP-over-TCP server.
    """
    @staticmethod
    def can_connect_to(location: str) -> bool:
        """Whether this client class can connect to the given location.

        Args:
            location: The location to potentially connect to.

        Returns:
            True iff this class can connect to this location.
        """
        return location.startswith('tcp:')

    def __init__(self, instance_id: Reference, location: str) -> None:
        """Create an MCPClient for a given location.

        The client will connect to this location and be able to request
        messages from any instance and port represented by it.

        Args:
            instance_id: Id of our instance.
            location: A location string for the peer.
        """
        super().__init__(instance_id, location)

        address = 'tcp://{}'.format(location.partition(':')[2])
        import pynng
        self._socket = pynng.Req0(dial=address)

    def receive(self, receiver: Reference) -> Message:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        self._socket.send(str(receiver).encode('utf-8'))

        databuf = self._socket.recv()

        message_dict = msgpack.unpackb(databuf, raw=False)
        return Message(
                Reference(message_dict['sender']),
                Reference(message_dict['receiver']),
                message_dict['port_length'],
                message_dict['timestamp'],
                message_dict['next_timestamp'],
                message_dict['parameter_overlay'],
                message_dict['data'])

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        self._socket.close()
