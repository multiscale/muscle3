import socketserver as ss
import threading
from typing import cast, List, Optional, Tuple
from typing_extensions import Type

import netifaces

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
                target=self._server.serve_forever, daemon=True)
        self._server_thread.start()

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        host, port = self._server.server_address

        locs = list()   # type: List[str]
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
        all_addresses = list()  # type: List[str]
        ifs = netifaces.interfaces()
        for interface in ifs:
            addrs = netifaces.ifaddresses(interface)
            for props in addrs.get(netifaces.AF_INET, []):
                if not props['addr'].startswith('127.'):
                    all_addresses.append(props['addr'])
            for props in addrs.get(netifaces.AF_INET6, []):
                # filter out link-local addresses with a scope id
                if '%' not in props['addr'] and props['addr'] != '::1':
                    all_addresses.append('[' + props['addr'] + ']')
        return all_addresses
