from errno import ENOTCONN
import select
import logging
import socket
from typing import Optional, Tuple

from libmuscle.mcp.transport_client import ProfileData, TransportClient, TimeoutHandler
from libmuscle.mcp.tcp_util import recv_all, recv_int64, send_int64
from libmuscle.profiling import ProfileTimestamp


_logger = logging.getLogger(__name__)


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

        sock: Optional[socket.SocketType] = None
        for address in addresses:
            try:
                sock = self._connect(address, False)
                break
            except RuntimeError:
                pass

        if sock is None:
            # None of our quick connection attempts worked. Either there's a network
            # problem, or the server is very busy. Let's try again with more patience.
            _logger.warning(
                    f'Could not immediately connect to {location}, trying again with'
                    ' more patience. Please report this if it happens frequently.')

            for address in addresses:
                try:
                    sock = self._connect(address, True)
                    break
                except RuntimeError:
                    pass

        if sock is None:
            _logger.error(f'Failed to connect also on the second try to {location}')
            raise RuntimeError('Could not connect to the server at location'
                               ' {}'.format(location))

        if hasattr(socket, "TCP_NODELAY"):
            sock.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        if hasattr(socket, "TCP_QUICKACK"):
            sock.setsockopt(socket.SOL_TCP, socket.TCP_QUICKACK, 1)
        self._socket = sock

        if hasattr(select, "poll"):
            self._poll_obj: Optional[select.poll] = select.poll()
            self._poll_obj.register(self._socket, select.POLLIN)
        else:
            self._poll_obj = None  # On platforms that don't support select.poll

    def call(self, request: bytes, timeout_handler: Optional[TimeoutHandler] = None
             ) -> Tuple[bytes, ProfileData]:
        """Send a request to the server and receive the response.

        This is a blocking call.

        Args:
            request: The request to send
            timeout_handler: Optional timeout handler. This is used for communication
                deadlock detection.

        Returns:
            The received response
        """
        start_wait = ProfileTimestamp()
        send_int64(self._socket, len(request))
        self._socket.sendall(request)

        did_timeout = False
        if timeout_handler is not None:
            while not self._poll(timeout_handler.timeout):
                did_timeout = True
                timeout_handler.on_timeout()

        length = recv_int64(self._socket)
        if did_timeout:
            assert timeout_handler is not None  # mypy
            timeout_handler.on_receive()
        start_transfer = ProfileTimestamp()

        response = recv_all(self._socket, length)
        stop_transfer = ProfileTimestamp()
        return response, (start_wait, start_transfer, stop_transfer)

    def _poll(self, timeout: float) -> bool:
        """Poll the socket and return whether its ready for receiving.

        This method blocks until the socket is ready for receiving, or :param:`timeout`
        seconds have passed (whichever is earlier).

        Args:
            timeout: timeout in seconds

        Returns:
            True if the socket is ready for receiving data, False otherwise.
        """
        if self._poll_obj is not None:
            ready = self._poll_obj.poll(timeout * 1000)  # poll timeout is in ms
        else:
            # Fallback to select()
            ready, _, _ = select.select([self._socket], (), (), timeout)
        return bool(ready)

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        try:
            self._socket.shutdown(socket.SHUT_RDWR)
            self._socket.close()
        except OSError as e:
            # This can happen if the peer has shut down already when we
            # close our connection to it, which is fine.
            if e.errno != ENOTCONN:
                raise

    def _connect(self, address: str, patient: bool) -> socket.SocketType:
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
                sock.settimeout(20.0 if patient else 3.0)     # seconds
                sock.connect(sockaddr)
                sock.settimeout(60.0)
            except Exception:
                sock.close()
                continue
            return sock

        raise RuntimeError('Could not connect')
