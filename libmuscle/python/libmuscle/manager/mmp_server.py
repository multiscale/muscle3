import errno
import logging
from typing import Any, cast, Generator, List

import msgpack
from ymmsl import Conduit, Identifier, Operator, Port, Reference, Settings

from libmuscle.logging import LogLevel
from libmuscle.manager.instance_registry import (
        AlreadyRegistered, InstanceRegistry)
from libmuscle.manager.logger import Logger
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mcp.transport_server import RequestHandler
from libmuscle.timestamp import Timestamp
from libmuscle.util import generate_indices, instance_indices


_logger = logging.getLogger(__name__)


def decode_operator(data: str) -> Operator:
    """Create an Operator from a MsgPack-compatible value."""
    return Operator[data]


def decode_port(data: List[str]) -> Port:
    """Create a Port from a MsgPack-compatible value."""
    return Port(Identifier(data[0]), decode_operator(data[1]))


def encode_conduit(conduit: Conduit) -> List[str]:
    """Convert a Conduit to a MsgPack-compatible value."""
    return [str(conduit.sender), str(conduit.receiver)]


class MMPRequestHandler(RequestHandler):
    """Handles Manager requests."""
    def __init__(
            self,
            logger: Logger,
            settings: Settings,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore):
        """Create an MMPRequestHandler.

        Args:
            logger: The Logger component to log messages to.
            settings: The global settings to serve to instances.
            instance_registry: The database for instances.
            topology_store: Keeps track of how to connect things.
        """
        self._logger = logger
        self._settings = settings
        self._instance_registry = instance_registry
        self._topology_store = topology_store

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
        if req_type == RequestType.REGISTER_INSTANCE.value:
            response = self._register_instance(*req_args)
        elif req_type == RequestType.GET_PEERS.value:
            response = self._get_peers(*req_args)
        elif req_type == RequestType.DEREGISTER_INSTANCE.value:
            response = self._deregister_instance(*req_args)
        elif req_type == RequestType.GET_SETTINGS.value:
            response = self._get_settings(*req_args)
        elif req_type == RequestType.SUBMIT_LOG_MESSAGE.value:
            response = self._submit_log_message(*req_args)
        elif req_type == RequestType.SUBMIT_PROFILE_EVENTS.value:
            response = self._submit_profile_events(*req_args)

        return cast(bytes, msgpack.packb(response, use_bin_type=True))

    def _register_instance(
            self, instance_id: str, locations: List[str],
            ports: List[List[str]]) -> Any:
        """Handle a register instance request.

        Args:
            instance_id: ID of the instance to register
            locations: Locations where it can be reached

        Returns:
            A list containing the following values:

            status (ResponseType): SUCCESS or ERROR
            error_msg (str): An error message, only present if status
                equals ERROR
        """
        port_objs = [decode_port(p) for p in ports]
        try:
            self._instance_registry.add(
                Reference(instance_id), locations, port_objs)

            _logger.info(f'Registered instance {instance_id}')
            return [ResponseType.SUCCESS.value]
        except AlreadyRegistered:
            return [
                    ResponseType.ERROR.value,
                    f'An instance with name {instance_id} was already'
                    ' registered. Did you start a non-MPI component using'
                    ' mpirun?']

    def _get_peers(self, instance_id: str) -> Any:
        """Handle a get peers request.

        Args:
            instance_id: ID of the instance requesting peers

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
            conduits (List[List[str]]): Conduits from/to peers
            dimensions (Dict[str, List[int]]): Dimensions of peer
                components
            locations (Dict[str, List[str]]): Locations where peer
                instances can be contacted.

            Or the following values on error:

            status (ResponseType): ERROR
            error_msg (str): An error message

            Or the following values if the result is not yet available:

            status (ResponseType): PENDING
            status_msg (str): A message on what we're waiting for.
        """
        # get info from yMMSL
        instance = Reference(instance_id)
        component = instance.without_trailing_ints()
        if not self._topology_store.has_kernel(component):
            return [ResponseType.ERROR.value, f'Unknown component {component}']

        conduits = self._topology_store.get_conduits(component)
        mmp_conduits = [encode_conduit(c) for c in conduits]

        peer_dims = self._topology_store.get_peer_dimensions(component)
        mmp_dimensions = {str(name): dims for name, dims in peer_dims.items()}

        # generate instances
        try:
            instance_locations = {
                    str(peer): self._instance_registry.get_locations(peer)
                    for peer in self._generate_peer_instances(instance)}
        except KeyError as e:
            return [
                    ResponseType.PENDING.value,
                    f'Waiting for component {e.args[0]}']

        _logger.debug(f'Sent peers to {instance_id}')
        return [
                ResponseType.SUCCESS.value,
                mmp_conduits, mmp_dimensions, instance_locations]

    def _deregister_instance(self, instance_id: str) -> Any:
        """Handle a deregister instance request.

        Args:
            instance_id: ID of the instance to deregister

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS

            Or the following if an error occurred:

            status (ResponseType): ERROR
            error_msg (str): An error message
        """
        try:
            self._instance_registry.remove(Reference(instance_id))
            _logger.info(f'Deregistered instance {instance_id}')
            return [ResponseType.SUCCESS.value]
        except ValueError:
            return [
                    ResponseType.ERROR.value,
                    f'No instance with name {instance_id} was registered']

    def _get_settings(self) -> Any:
        """Handle a get settings request.

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
            settings (Dict[str, SettingValue]): The global settings
        """
        return [
                ResponseType.SUCCESS.value,
                self._settings.as_ordered_dict()]

    def _submit_log_message(
            self, instance_id: str, timestamp: float, level: int, text: str
            ) -> Any:
        """Handle a submit log message request.

        Args:
            instance_id: Sending instance
            timestamp: Time since epoch of the logged event
            level: Log level of the message
            text: Message text

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
        """
        self._logger.log_message(
                instance_id, Timestamp(timestamp), LogLevel(level), text)
        return [ResponseType.SUCCESS.value]

    def _submit_profile_events(self, events: List[List[Any]]) -> Any:
        """Handle a submit profile events request.

        Not implemented yet.

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
        """
        return [ResponseType.SUCCESS.value]

    def _generate_peer_instances(
            self, instance: Reference) -> Generator[Reference, None, None]:
        """Generates the names of all peer instances of an instance.

        Args:
            instance: The instance whose peers to generate.

        Yields:
            All peer instance identifiers.
        """
        component = instance.without_trailing_ints()
        indices = instance_indices(instance)
        dims = self._topology_store.kernel_dimensions[component]
        all_peer_dims = self._topology_store.get_peer_dimensions(component)
        for peer, peer_dims in all_peer_dims.items():
            base = peer
            for i in range(min(len(dims), len(peer_dims))):
                base += indices[i]

            if dims >= peer_dims:
                yield base
            else:
                for peer_indices in generate_indices(peer_dims[len(dims):]):
                    yield base + peer_indices


class MMPServer:
    """The MUSCLE Manager Protocol server.

    This class accepts connections from the instances comprising
    the multiscale model to be executed, and services them using an
    MMPRequestHandler.
    """
    def __init__(
            self,
            logger: Logger,
            settings: Settings,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore
            ) -> None:
        """Create an MMPServer.

        This starts a TCP Transport server and connects it to an
        MMPRequestHandler, which uses the given components to service
        the requests. By default, we listen on port 9000, unless it's
        not available in which case we use a random other one.

        Args:
            logger: Logger to send log messages to
            settings: Settings component to get settings from
            instance_registry: To register instances with and get
                peer locations from
            topology_store: To get peers and conduits from
        """
        self._handler = MMPRequestHandler(
                logger, settings, instance_registry, topology_store)
        try:
            self._server = TcpTransportServer(self._handler, 9000)
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

        This makes the server stop serving requests, and shuts down its
        background threads.
        """
        self._server.close()
