import threading
from typing import Optional, Tuple


class SessionState:
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
        """Create a SessionState object.

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
            return f'SessionState({self._cur_request}, {self._response is not None})'

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
        """Set the response and notify that we're done.

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

        Args:
            response: A newly generated response
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
