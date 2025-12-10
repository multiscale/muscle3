import errno
import logging
from typing import Any, Dict, List, Tuple, cast

import msgpack
from ymmsl import Reference

from libmuscle.manager.logger import Logger
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mcp.transport_server import RequestHandler
from libmuscle.profiling import (ProfileTimestamp, ProfileEvent,
                                 ProfileEventType)


_logger = logging.getLogger(__name__)


class MLPRequestHandler(RequestHandler):
    """Handles Manager requests."""
    def __init__(
            self,
            logger: Logger,
            profile_store: ProfileStore
            ) -> None:
        """Create an MLPRequestHandler.

        Args:
            logger: The Logger component to log messages to.
            profile_store: The profile store to store profile events in.
        """
        self._logger = logger
        self._profile_store = profile_store

    def handle_request(self, request: bytes) -> bytes:
        """Handles a manager request.

        Args:
            request: The encoded request

        Returns:
            response: An encoded response
        """
        req_list = msgpack.unpackb(request, raw=False)
        req_type = req_list[0]
        req_args = req_list[1:]
        if req_type == RequestType.REPORT_USAGE.value:
            response = self._report_usage_events(*req_args)

        return cast(bytes, msgpack.packb(response, use_bin_type=True))

    def close(self) -> None:
        """Free per-thread resources.

        On shutdown of the server, this will be called by each server
        thread before it shuts down.
        """
        self._profile_store.close()

    def _report_usage_events(
            self, node_name: str, usage: Dict[str, Tuple[float, int]]) -> Any:
        """Handle a submit usage events request.

        Args:
            node_name: Name of the node that sent these events
            usage: Usage events to store

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
        """
        events: List[Tuple[str, ProfileEvent]] = []
        for instance_id, (cpu_usage, memory_usage) in usage.items():
            time = ProfileTimestamp()
            prof_event = ProfileEvent(ProfileEventType.RESOURCE_USAGE,
                                      start_time=time, stop_time=time,
                                      cpu_percent=cpu_usage, memory_usage=memory_usage)
            events.append((instance_id, prof_event))

        for event in events:
            self._profile_store.add_event(Reference(event[0]), event[1])

        return [ResponseType.SUCCESS.value]


class MLPServer:
    """The MUSCLE Logging Protocol server.

    This class accepts connections from the instances comprising
    the multiscale model to be executed, and services them using an
    MLPRequestHandler.
    """
    def __init__(
            self,
            logger: Logger,
            profile_store: ProfileStore
            ) -> None:
        """Create an MLPServer.

        This starts a TCP Transport server and connects it to an
        MLPRequestHandler, which uses the given components to service
        the requests. By default, we listen on port 9001, unless it's
        not available in which case we use a random other one.

        Args:
            logger: Logger to send log messages to
            profile_store: ProfileStore to store profile data in
        """
        self._handler = MLPRequestHandler(logger, profile_store)
        try:
            self._server = TcpTransportServer(self._handler, 9001)
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise
            self._server = TcpTransportServer(self._handler)

    def get_location(self) -> str:
        """Returns this server's network location.

        This is a string of the form tcp:<hostname>:<port>.
        """
        return self._server.get_location()

    def stop(self) -> None:
        """Stops the server.

        This makes the server stop serving requests, and shuts down its background
        threads. By the time this gets called, the instances are down, so we don't need
        to wait for any sessions to time out.
        """
        self._server.close(False)
