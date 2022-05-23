import socket
from typing import Optional

from libmuscle.mcp.transport_client import TransportClient
from libmuscle.mcp.tcp_util import recv_all, recv_int64, send_int64


class TcpTransportClient(TransportClient):
    """A client that connects to a TCPTransport server.
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

    def __init__(self, location: str) -> None:
        """Create a TcpClient for a given location.

        The client will connect to this location and be able to request
        messages from any instance and port represented by it.

        Args:
            location: A location string for the peer.
        """
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

    def call(self, request: bytes) -> bytes:
        """Send a request to the server and receive the response.

        This is a blocking call.

        Args:
            request: The request to send

        Returns:
            The received response
        """
        send_int64(self._socket, len(request))
        self._socket.sendall(request)

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
