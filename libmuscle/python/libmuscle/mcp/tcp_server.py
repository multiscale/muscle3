import socketserver as ss
import threading
from typing import cast, List, Optional, Tuple
from typing_extensions import Type

import netifaces
from ymmsl import Reference

from libmuscle.mcp.server import Server
from libmuscle.mcp.tcp_util import (recv_all, recv_int64, send_int64,
                                    SocketClosed)
from libmuscle.post_office import PostOffice


class TcpServerImpl(ss.ThreadingMixIn, ss.TCPServer):
    daemon_threads = True

    def __init__(self, host_port_tuple: Tuple[str, int],
                 streamhandler: Type, tcp_server: 'TcpServer'
                 ) -> None:
        super().__init__(host_port_tuple, streamhandler)
        self.tcp_server = tcp_server


class TcpHandler(ss.BaseRequestHandler):
    """Handler for MCP-over-TCP connections.
    """
    def handle(self) -> None:
        """Handles requests on a socket
        """
        receiver_id = self.receive_request()

        while receiver_id is not None:
            server = cast(TcpServerImpl, self.server).tcp_server
            message = server.post_office.get_message(receiver_id)

            send_int64(self.request, len(message))
            self.request.sendall(message)
            receiver_id = self.receive_request()

    def receive_request(self) -> Optional[Reference]:
        """Receives a request (receiver id).

        Returns:
            The received receiver id.
        """
        try:
            length = recv_int64(self.request)
            reqbuf = recv_all(self.request, length)
            return Reference(reqbuf.decode('utf-8'))
        except SocketClosed:
            return None


class TcpServer(Server):
    """A server that accepts MCP connections over TCP.
    """
    def __init__(self, instance_id: Reference, post_office: PostOffice
                 ) -> None:
        """Create a TCPServer.

        Args:
            instance_id: Id of the instance we're a server for.
            post_office: A PostOffice to obtain data from.
        """
        super().__init__(instance_id, post_office)

        self._server = TcpServerImpl(('', 0), TcpHandler, self)
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

    @property
    def post_office(self) -> PostOffice:
        """Export this so the server thread can use it.
        """
        return self._post_office

    def _get_if_addresses(self) -> List[str]:
        all_addresses = list()  # type: List[str]
        ifs = netifaces.interfaces()
        for interface in ifs:
            addrs = netifaces.ifaddresses(interface)
            for props in addrs.get(netifaces.AF_INET, []):
                all_addresses.append(props['addr'])
            for props in addrs.get(netifaces.AF_INET6, []):
                # filter out link-local addresses with a scope id
                if '%' not in props['addr']:
                    all_addresses.append('[' + props['addr'] + ']')
        return all_addresses
