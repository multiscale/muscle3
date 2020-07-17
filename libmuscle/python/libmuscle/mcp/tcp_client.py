import socket

from typing import Optional
from ymmsl import Reference

from libmuscle.mcp.client import Client
from libmuscle.mcp.tcp_util import recv_all, recv_int64, send_int64


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
        """Create a TcpClient for a given location.

        The client will connect to this location and be able to request
        messages from any instance and port represented by it.

        Args:
            instance_id: Id of our instance.
            location: A location string for the peer.
        """
        super().__init__(instance_id, location)

        addresses = location[4:].split(',')

        sock = None     # type: Optional[socket.SocketType]
        for address in addresses:
            try:
                sock = self._connect(address)
                break
            except RuntimeError:
                pass

        if sock is None:
            raise RuntimeError('Could not connect to the server at location'
                               ' {}'.format(location))
        else:
            self._socket = sock

    def receive(self, receiver: Reference) -> bytes:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        receiver_str = str(receiver).encode('utf-8')
        send_int64(self._socket, len(receiver_str))
        self._socket.sendall(receiver_str)

        length = recv_int64(self._socket)
        return recv_all(self._socket, length)

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        self._socket.shutdown(socket.SHUT_RDWR)
        self._socket.close()

    def _connect(self, address: str) -> socket.SocketType:
        loc_parts = address.rsplit(':', 1)
        host = loc_parts[0]
        if host.startswith('['):
            if host.endswith(']'):
                host = host[1:-1]
            else:
                raise RuntimeError('Invalid address')
        port = int(loc_parts[1])

        addrinfo = socket.getaddrinfo(
                host, port, 0, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        for family, socktype, proto, _, sockaddr in addrinfo:
            try:
                sock = socket.socket(family, socktype, proto)
            except Exception:
                continue

            try:
                sock.connect(sockaddr)
            except Exception:
                sock.close()
                continue
            return sock

        raise RuntimeError('Could not connect')
