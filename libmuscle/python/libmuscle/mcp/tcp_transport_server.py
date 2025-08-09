import logging
import socket
import socketserver as ss
import threading
from typing import Any, cast, Dict, List, Tuple, Type

import psutil

from libmuscle.mcp.session_state import SessionState
from libmuscle.mcp.transport_server import RequestHandler, TransportServer
from libmuscle.mcp.tcp_util import (
        is_disconnect, recv_frame, recv_int64, send_frame, send_int64)


_logger = logging.getLogger(__name__)


class TcpTransportServerImpl(ss.ThreadingMixIn, ss.TCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(self, host_port_tuple: Tuple[str, int],
                 streamhandler: Type, transport_server: 'TcpTransportServer'
                 ) -> None:
        super().__init__(host_port_tuple, streamhandler)
        self.transport_server = transport_server
        if hasattr(socket, "TCP_NODELAY"):
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_NODELAY, 1)
        if hasattr(socket, "TCP_QUICKACK"):
            self.socket.setsockopt(socket.SOL_TCP, socket.TCP_QUICKACK, 1)

        self.session_store: Dict[int, SessionState] = dict()
        self.session_lock = threading.Lock()
        self.next_session = 1


class TcpHandler(ss.BaseRequestHandler):
    """Handler for MCP-over-TCP connections.

    This is a Python handler for Python's TCPServer, which forwards
    to the RequestHandler attached to the server.

    There's a small terminology issue here: Python calls an entire connection a request,
    so self.request actually refers to the current connection we're servicing. We're
    doing Remote Procedure Call over that, and we call every RPC call we receive from
    the client a request also.
    """
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._session_id = 0
        super().__init__(*args, **kwargs)

    def handle(self) -> None:
        """Handles connections, one per call"""
        server = cast(TcpTransportServerImpl, self.server)

        try:
            self._start_session()

            while True:
                request_nr = recv_int64(self.request)
                request = recv_frame(self.request)

                should_process, should_send = self._session_state.triage_request(
                        request_nr)

                if should_process:
                    response = server.transport_server._handler.handle_request(request)
                    self._session_state.set_response(response)

                if should_send:
                    response_to_send = self._session_state.wait_get_response(request_nr)
                    if response_to_send is not None:
                        send_frame(self.request, response_to_send)

        except Exception as e:
            if not is_disconnect(e):
                raise

    def _start_session(self) -> None:
        """(Re)starts a session

        Sessions are identified by a number, which we create and which we and the client
        both store. If we get disconnected, the client can reconnect with that session
        id, so that we can resend whatever we were sending when we were rudely
        interrupted.

        Sets self._session_id to the obtained session id.
        """
        req_session_id = recv_int64(self.request)

        server = cast(TcpTransportServerImpl, self.server)
        if req_session_id == 0:
            with server.session_lock:
                self._session_id = server.next_session
                server.session_store[self._session_id] = SessionState()
                self._session_state = server.session_store[self._session_id]
                server.next_session += 1

            send_int64(self.request, self._session_id)

        else:
            _logger.warning(
                    f'The TCP network connection for session {req_session_id} was lost')

            with server.session_lock:
                if req_session_id not in server.session_store:
                    raise RuntimeError(f'Unknown session {req_session_id} requested')
                self._session_state = server.session_store[req_session_id]

            self._session_id = req_session_id
            send_int64(self.request, self._session_id)
            _logger.warning(f'Resuming session {self._session_id}')

    def finish(self) -> None:
        """Called when shutting down the thread?"""
        server = cast(TcpTransportServerImpl, self.server).transport_server
        server._handler.close()


class TcpTransportServer(TransportServer):
    """A TransportServer that uses TCP to communicate."""
    def __init__(self, handler: RequestHandler, port: int = 0) -> None:
        """Create a TCPServer.

        Args:
            handler: A RequestHandler to handle requests
            port: The port to use.

        Raises:
            OSError: With errno set to errno.EADDRINUSE if the port is not
                available.
        """
        super().__init__(handler)

        self._server = TcpTransportServerImpl(('', port), TcpHandler, self)
        self._server_thread = threading.Thread(
                target=self._server.serve_forever, args=(0.1,), daemon=True)
        self._server_thread.start()

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        host, port = self._server.server_address

        locs: List[str] = []
        for address in self._get_if_addresses():
            locs.append('{}:{}'.format(address, port))
        return 'tcp:{}'.format(','.join(locs))

    def close(self) -> None:
        """Closes this server.

        Stops the server listening, waits for existing clients to
        disconnect, then frees any other resources.
        """
        self._server.shutdown()
        self._server_thread.join()
        self._server.server_close()

    def _get_if_addresses(self) -> List[str]:
        """Returns a list of local addresses.

        This returns a list of strings containing all IPv4 and IPv6 network
        addresses bound to the available network interfaces. The server
        will listen on all interfaces, but not all of them may be reachable
        from the client. So we get all of them here, and the client can
        then try them all and find one that works.
        """
        all_addresses: List[str] = []
        ifs = psutil.net_if_addrs()
        for _, addresses in ifs.items():
            for addr in addresses:
                if addr.family == socket.AF_INET:
                    if not addr.address.startswith('127.'):
                        all_addresses.append(addr.address)
                if addr.family == socket.AF_INET6:
                    # filter out link-local addresses with a scope id
                    if '%' not in addr.address and addr.address != '::1':
                        all_addresses.append('[' + addr.address + ']')

        return all_addresses
