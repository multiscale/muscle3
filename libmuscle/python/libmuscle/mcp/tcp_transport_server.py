import socket
import socketserver as ss
import threading
from typing import cast, List, Optional, Tuple, Type

import psutil

from libmuscle.mcp.transport_server import RequestHandler, TransportServer
from libmuscle.mcp.tcp_util import (recv_all, recv_int64, send_int64,
                                    SocketClosed)


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


class TcpHandler(ss.BaseRequestHandler):
    """Handler for MCP-over-TCP connections.

    This is a Python handler for Python's TCPServer, which forwards
    to the RequestHandler attached to the server.
    """
    def handle(self) -> None:
        """Handles requests on a socket
        """
        request = self.receive_request()

        while request is not None:
            server = cast(TcpTransportServerImpl, self.server).transport_server
            response = server._handler.handle_request(request)

            send_int64(self.request, len(response))
            self.request.sendall(response)
            request = self.receive_request()

    def receive_request(self) -> Optional[bytes]:
        """Receives a request

        Returns:
            The received bytes
        """
        try:
            length = recv_int64(self.request)
            reqbuf = recv_all(self.request, length)
            return reqbuf
        except SocketClosed:
            return None

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
