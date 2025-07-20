import logging
import socket
import socketserver as ss
import threading
from typing import Any, cast, Dict, List, Optional, Tuple, Type

import psutil

from libmuscle.mcp.transport_server import RequestHandler, TransportServer
from libmuscle.mcp.tcp_util import (is_disconnect, recv_all, recv_int64, send_int64)


_logger = logging.getLogger(__name__)


class RpcState:
    """Tracks the state of an RPC session.

    Our TCP server is multithreaded, spawning a thread for every active connection. If a
    connection is lost, then the thread will die, but only when it realises that the
    connection is gone, and that only happens during a send or receive.

    It's therefore possible to have multiple threads for the same session at the same
    time, if the client has detected a broken connection and reconnected (to a new
    thread) while the existing thread on the server is still processing the request, and
    will only discover the broken connection when it tries to send the result.

    This class facilitates collaboration between those threads, making sure that each
    request is processed exactly once, and that the response continues to be available
    until the client has successfully received it.

    A connection can be in two states: 1) request n has been received and is being
    processed, and 2) request n has been received and has been processed so that
    response n can be sent. We transition from 1) to 2) when processing of request n
    completes, and we transition from 2) back to 1) when request n+1 is received, at
    which point n is incremented and we're back to 1). The response is sent during 2),
    but sending it doesn't itself change the state, because a TCP send just puts the
    data in a local buffer and we can't tell whether it'll actually reach the receiver.

    Objects of this class therefore store n, the most recently received request, and, if
    and only if we're in state 2), response n.
    """
    def __init__(self) -> None:
        """Create an RPCState object.

        The first request will be 1, so we initialise to a state in which request 0 has
        seemingly been processed already and we're ready to do number 1 next.
        """
        # This contains a lock that protects self._cur_request and self._response (but
        # not what it points to) as well.
        self._response_ready = threading.Condition()

        self._cur_request = 0
        self._response: Optional[bytes] = bytes()

    def __str__(self) -> str:
        with self._response_ready:
            return f'RPCState({self._cur_request}, {self._response is not None})'

    def __repr__(self) -> str:
        return self.__str__()

    def triage_request(self, request_nr: int) -> Tuple[bool, bool]:
        """Decide what to do about an incoming request

        This returns a tuple (should_process, should_send) that tells the handler
        thread, given the current state of the connection, whether it should try to
        process the request, and whether it should try to send the result.

        When request n is received, then we know that any requests before that have been
        completed successfully, because the client won't send request n until after it's
        received the response for n-1 in good order. Therefore, if the current request
        is n-1 and we receive request n, then we can delete the response for n-1, set
        the current request to n, and start processing.

        If we receive request n while n is already the current request, then this is a
        re-request submitted to a new handling thread because the client encountered an
        error either during a previous send of request n or receive of response n, and
        is trying again. In that case, another thread is already processing the request,
        and we should wait for a response to be available and send it. (The thread doing
        the processing will have a broken connection, so it will fail on sending and
        quit.) If we also fail to send due to another disconnect, then the client will
        make another request and there will be a new thread to try to send the response
        again, until it succeeds.

        If we receive a request with number < n, then this is an old request that was
        received previously, but then the thread got suspended for a while and the
        connection broke, so the client tried again and it was handled by another
        thread, and now this one is way behind. In that case, we do nothing and quit.

        If we receive a request n+2 or more while the current request is n, then the
        client is skipping numbers or sending them out of order, so that shouldn't
        happen.

        To summarise: there are three possible options: under normal conditions the
        request should be processed and the response sent. If this is a re-request, then
        another thread will be processing already and we just need to send the response
        when it becomes available. If the request is old and has already been completed
        successfully, then we neither process nor request.

        Note that request numbers may wrap, in which case this will crash or hang. At a
        rate of 1000 requests per second, this will take a bit under 3 million years, so
        it shouldn't be an issue except for astrophysics simulations, but then those
        should just use AMUSE anyway.

        Args:
            request_nr: The request number of the received request

        Returns:
            Whether to try to process the request, and whether to try to send the
            response.
        """
        with self._response_ready:
            should_process = (
                    self._response is not None and self._cur_request < request_nr)
            if should_process:
                self._cur_request = request_nr
                self._response = None

            should_send = self._cur_request == request_nr

            return should_process, should_send

    def set_response(self, response: bytes) -> None:
        """Notify that we're done and set the response.

        This sets the response and notifies any threads waiting in wait_get_response()
        that one is available.

        If a connection is lost while we're waiting for a response to become available,
        then there are two threads: one with a dead connection that's still doing the
        processing, and one with a working connection that should send the result. If
        the connection breaks again, then there will be another one.

        When the work is done, we wake up all threads and have them all try to send,
        only the one with the working connection will succeed and continue, the rest
        will fail and quit. Or maybe all of them fail, in which case the client will
        have to send another request to try again.
        """
        with self._response_ready:
            self._response = response
            self._response_ready.notify_all()

    def wait_get_response(self, request_nr: int) -> Optional[bytes]:
        """Wait for a response to be available and return it

        It shouldn't be possible for anyone to be waiting for response n while response
        n-1 isn't available yet, but it is possible to be waiting for response n while
        that response has already been returned and we're processing n+1 or later. In
        that case we return None, signalling that that response no longer exists and
        doesn't need to be sent again. The send would fail anyway because if the client
        moved on then it was because our connection is broken.

        Returns:
            The response for the current request, or None if it's no longer available.
        """
        with self._response_ready:
            while self._cur_request <= request_nr:
                while self._response is None:
                    self._response_ready.wait()

                if self._cur_request == request_nr:
                    return self._response

            return None


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

        self.session_store: Dict[int, RpcState] = dict()
        self.session_lock = threading.Lock()
        self.next_session = 1


class TcpHandler(ss.BaseRequestHandler):
    """Handler for MCP-over-TCP connections.

    This is a Python handler for Python's TCPServer, which forwards
    to the RequestHandler attached to the server.

    There's a small terminology issue here: Python calls an entire connection a request,
    so self.request actually refers to the current connection we're servicing. We're
    doing Remote Procedure Call over that, and we call every RPC call we receive from
    the client a request, and that's what _receive_request() is about.
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
                request_nr, request = self._receive_request()

                should_process, should_send = self._rpc_state.triage_request(request_nr)

                if should_process:
                    response = server.transport_server._handler.handle_request(request)
                    self._rpc_state.set_response(response)

                if should_send:
                    response_to_send = self._rpc_state.wait_get_response(request_nr)
                    if response_to_send is not None:
                        self._send_response(response_to_send)

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
                server.session_store[self._session_id] = RpcState()
                self._rpc_state = server.session_store[self._session_id]
                server.next_session += 1

            send_int64(self.request, self._session_id)

        else:
            _logger.warning(
                    f'The TCP network connection for session {req_session_id} was lost')

            with server.session_lock:
                if req_session_id not in server.session_store:
                    raise RuntimeError(f'Unknown session {req_session_id} requested')
                self._rpc_state = server.session_store[req_session_id]

            self._session_id = req_session_id
            send_int64(self.request, self._session_id)
            _logger.warning(f'Resuming session {self._session_id}')

    def _receive_request(self) -> Tuple[int, bytes]:
        """Receives a request

        Returns:
            The request number and the received bytes
        """
        request_number = recv_int64(self.request)
        length = recv_int64(self.request)
        reqbuf = recv_all(self.request, length)
        return request_number, reqbuf

    def _send_response(self, response: bytes) -> None:
        """Send a response

        Args:
            response: The response to send
        """
        send_int64(self.request, len(response))
        self.request.sendall(response)

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
