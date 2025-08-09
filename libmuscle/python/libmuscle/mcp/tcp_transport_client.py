import select
import logging
import socket
import time
from typing import Optional, Tuple

from libmuscle.mcp.transport_client import ProfileData, TransportClient, TimeoutHandler
from libmuscle.mcp.tcp_util import (
        is_disconnect, recv_frame, recv_int64, send_frame, send_int64)
from libmuscle.profiling import ProfileTimestamp
from libmuscle.util import Retrier


_logger = logging.getLogger(__name__)


_CONNECT_TIMEOUT = 3.0                      # seconds
_CONNECT_TIMEOUT_PATIENT = 60.0             # seconds
_CONNECT_TIMEOUT_PATIENT_STEP = 3.0         # seconds
_RECONNECT_TIMEOUT = 60.0                   # seconds


class NoPendingResponse(RuntimeError):
    pass


class TcpTransportClient(TransportClient):
    """A client that connects to a TCPTransport server."""
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

        The client will connect to this location and be able to send requests to it and
        return the response.

        Args:
            location: A location string for the peer.
        """
        self._addresses = location[4:].split(',')
        self._socket: Optional[socket.SocketType] = None
        self._session = 0
        self._cur_request = 0

        self._reconnect(False)

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
        self._cur_request += 1
        retrier = Retrier(_RECONNECT_TIMEOUT)
        while True:
            try:
                start_wait = ProfileTimestamp()
                if self._socket is None:
                    raise ConnectionError('No connection could be established')

                send_int64(self._socket, self._cur_request)
                send_frame(self._socket, request)

                did_timeout = False
                if timeout_handler is not None:
                    while not self._poll(timeout_handler.timeout):
                        did_timeout = True
                        timeout_handler.on_timeout()

                if did_timeout:
                    assert timeout_handler is not None  # mypy
                    timeout_handler.on_receive()

                start_transfer = ProfileTimestamp()
                response = recv_frame(self._socket)
                stop_transfer = ProfileTimestamp()
                return response, (start_wait, start_transfer, stop_transfer)

            except Exception as e:
                if is_disconnect(e):
                    self._handle_disconnect(retrier)
                else:
                    raise

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and performs other shutdown
        activities as needed.
        """
        try:
            if self._socket is not None:
                self._socket.shutdown(socket.SHUT_RDWR)
                self._socket.close()
        except Exception as e:
            # This can raise if the peer has shut down already when we close our
            # connection to it, which is fine and can be ignored. Otherwise, we reraise.
            if not is_disconnect(e):
                raise

    def _poll(self, timeout: float) -> bool:
        """Poll the socket and return whether its ready for receiving.

        This method blocks until the socket is ready for receiving, or :param:`timeout`
        seconds have passed (whichever is earlier).

        Args:
            timeout: timeout in seconds

        Returns:
            True if the socket is ready for receiving data, False otherwise.
        """
        retrier = Retrier()
        while True:
            try:
                if self._poll_obj is not None:
                    ready = self._poll_obj.poll(timeout * 1000)  # poll timeout is in ms
                else:
                    # Fallback to select()
                    ready, _, _ = select.select([self._socket], (), (), timeout)
                return bool(ready)

            except Exception as e:
                if is_disconnect(e):
                    self._handle_disconnect(retrier)
                else:
                    raise

    def _handle_disconnect(self, retrier: Retrier) -> None:
        """Handles a broken network connection.

        Args:
            retrier: A Retrier that keeps track of timing any retries
        """
        _logger.warning(
                f'The TCP network connection with {self._addresses} was lost'
                ' unexpectedly.')

        try:
            self.close()
        except Exception as e:
            if not is_disconnect(e):
                raise

        if retrier.should_give_up():
            _logger.warning(
                    f'I am unable to reconnect to {self._addresses} despite repeated'
                    ' attempts, and I am giving up. Please check your network.')
            raise

        retrier.sleep()

        _logger.warning(f'Trying to reconnect to {self._addresses}')

        self._reconnect()

    def _reconnect(self, re: bool = True) -> None:
        """(Re)connect to the server and resume the current session

        Args:
            re: True if this is a reconnect rather than an initial connect.
        """
        try:
            self._make_connection()
            assert self._socket is not None
            send_int64(self._socket, self._session)
            self._session = recv_int64(self._socket)

            if re:
                _logger.warning(
                        f'Reconnected to {self._addresses}, continuing the'
                        ' simulation')

        except Exception as e:
            if is_disconnect(e):
                self.close()
                _logger.warning(
                        f'Failed to reconnect to {self._addresses}, will retry'
                        ' later')
            else:
                raise

    def _make_connection(self) -> None:
        """Connect to the server and set up polling

        Uses self._addresses and creates a (new) self._socket and self._poll_obj.
        """
        sock: Optional[socket.SocketType] = None
        for address in self._addresses:
            try:
                sock = self._connect(address, False)
                break
            except RuntimeError:
                pass

        if sock is None:
            # None of our quick connection attempts worked. Either there's a network
            # problem, or the server is very busy. Let's try again with more patience.
            _logger.warning(
                    f'Could not immediately connect to {self._addresses}, trying again'
                    ' with more patience. Please report this if it happens frequently.')

            for address in self._addresses:
                try:
                    _logger.debug(
                            f'Trying to connect to {address} patiently')
                    sock = self._connect(address, True)
                    break
                except RuntimeError:
                    pass

        if sock is None:
            _logger.error(
                    f'Failed to connect also on the second try to {self._addresses}')
            raise ConnectionRefusedError(
                    f'Could not connect to any server at locations {self._addresses}')

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

    def _connect(self, address: str, patient: bool) -> socket.SocketType:
        loc_parts = address.rsplit(':', 1)
        host = loc_parts[0]
        if host.startswith('['):
            if host.endswith(']'):
                host = host[1:-1]
            else:
                raise RuntimeError('Invalid address')
        port = int(loc_parts[1])

        timeout = _CONNECT_TIMEOUT_PATIENT if patient else _CONNECT_TIMEOUT
        patient_step = _CONNECT_TIMEOUT_PATIENT_STEP

        addrinfo = socket.getaddrinfo(
                host, port, 0, socket.SOCK_STREAM, socket.IPPROTO_TCP)

        for family, socktype, proto, _, sockaddr in addrinfo:
            try:
                sock = socket.socket(family, socktype, proto)
            except Exception:
                continue

            start_time = time.monotonic()
            time_left = (start_time + timeout) - time.monotonic()
            while (time_left > 0.0):
                try:
                    sock.settimeout(time_left)
                    sock.connect(sockaddr)
                    sock.settimeout(None)
                    return sock
                except (ConnectionRefusedError, ConnectionAbortedError):
                    if patient:
                        _logger.warning('Connection refused, sleeping')
                        time.sleep(patient_step)
                    else:
                        _logger.info(f'Failed to connect to {sockaddr}')
                        sock.close()
                        break

                except Exception as e:
                    _logger.debug(f'Failed to connect socket: {e}')
                    sock.close()
                    break

                time_left = (start_time + timeout) - time.monotonic()

        raise RuntimeError('Could not connect')
