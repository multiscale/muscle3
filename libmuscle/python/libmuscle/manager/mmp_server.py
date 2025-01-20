import errno
import logging
import time
from typing import Any, Dict, cast, List, Optional

import msgpack
from ymmsl import (
        Conduit, Identifier, Operator, Port, Reference, PartialConfiguration,
        Checkpoints, CheckpointRule, CheckpointAtRule, CheckpointRangeRule)

import libmuscle
from libmuscle.logging import LogLevel
from libmuscle.manager.instance_registry import (
        AlreadyRegistered, InstanceRegistry)
from libmuscle.manager.logger import Logger
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.snapshot_registry import SnapshotRegistry
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mcp.transport_server import RequestHandler
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.manager.deadlock_detector import DeadlockDetector
from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)
from libmuscle.snapshot import SnapshotMetadata
from libmuscle.timestamp import Timestamp


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


def encode_checkpoint_rule(rule: CheckpointRule) -> Dict[str, Any]:
    """Convert a CheckpointRule to a MsgPack-compatible value."""
    if isinstance(rule, CheckpointAtRule):
        return {'at': list(map(float, rule.at))}
    if isinstance(rule, CheckpointRangeRule):
        return {
            'start': None if rule.start is None else float(rule.start),
            'stop': None if rule.stop is None else float(rule.stop),
            'every': float(rule.every)}
    raise TypeError(f"Unknown checkpoint rule type: {type(rule)}.")


def encode_checkpoints(checkpoints: Checkpoints) -> Dict[str, Any]:
    """Convert a Checkpoins to a MsgPack-compatible value."""
    return {
        "at_end": checkpoints.at_end,
        "wallclock_time":
            list(map(encode_checkpoint_rule, checkpoints.wallclock_time)),
        "simulation_time":
            list(map(encode_checkpoint_rule, checkpoints.simulation_time)),
    }


class MMPRequestHandler(RequestHandler):
    """Handles Manager requests."""
    def __init__(
            self,
            logger: Logger,
            profile_store: ProfileStore,
            configuration: PartialConfiguration,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore,
            snapshot_registry: SnapshotRegistry,
            deadlock_detector: DeadlockDetector,
            run_dir: Optional[RunDir]
            ) -> None:
        """Create an MMPRequestHandler.

        Args:
            logger: The Logger component to log messages to.
            settings: The global settings to serve to instances.
            instance_registry: The database for instances.
            topology_store: Keeps track of how to connect things.
        """
        self._logger = logger
        self._profile_store = profile_store
        self._configuration = configuration
        self._instance_registry = instance_registry
        self._topology_store = topology_store
        self._snapshot_registry = snapshot_registry
        self._deadlock_detector = deadlock_detector
        self._run_dir = run_dir
        self._reference_time = time.monotonic()

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
        elif req_type == RequestType.SUBMIT_SNAPSHOT.value:
            response = self._submit_snapshot(*req_args)
        elif req_type == RequestType.GET_CHECKPOINT_INFO.value:
            response = self._get_checkpoint_info(*req_args)
        elif req_type == RequestType.WAITING_FOR_RECEIVE.value:
            response = self._waiting_for_receive(*req_args)
        elif req_type == RequestType.WAITING_FOR_RECEIVE_DONE.value:
            response = self._waiting_for_receive_done(*req_args)
        elif req_type == RequestType.IS_DEADLOCKED.value:
            response = self._is_deadlocked(*req_args)

        return cast(bytes, msgpack.packb(response, use_bin_type=True))

    def close(self) -> None:
        """Free per-thread resources.

        On shutdown of the server, this will be called by each server
        thread before it shuts down.
        """
        self._profile_store.close()

    def _register_instance(
            self, instance_id: str, locations: List[str],
            ports: List[List[str]], version: str = '') -> Any:
        """Handle a register instance request.

        Args:
            instance_id: ID of the instance to register
            locations: Locations where it can be reached
            ports: Ports of this instance
            version: Version of libmuscle that this instance uses

        Returns:
            A list containing the following values:

            status (ResponseType): SUCCESS or ERROR
            error_msg (str): An error message, only present if status
                equals ERROR
        """
        if version != libmuscle.__version__:
            return [
                    ResponseType.ERROR.value,
                    f'Instance libmuscle version ({version}) does not match'
                    f' manager libmuscle version ({libmuscle.__version__}).'
                    ' Please ensure that the instance and the manager use the'
                    ' same version of libmuscle.']

        port_objs = [decode_port(p) for p in ports]
        instance = Reference(instance_id)
        try:
            self._instance_registry.add(instance, locations, port_objs)

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
            peers = self._topology_store.get_peer_instances(instance)
            instance_locations = {
                    str(peer): self._instance_registry.get_locations(peer)
                    for peer in peers}
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
                self._configuration.settings.as_ordered_dict()]

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

    def _submit_profile_events(
            self, instance_id: str, events: List[List[Any]]) -> Any:
        """Handle a submit profile events request.

        Args:
            instance_id: Instance that sent these events
            events: Profiling events to store

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
        """
        ev = [
                ProfileEvent(
                    ProfileEventType(e[0]), ProfileTimestamp(e[1]),
                    ProfileTimestamp(e[2]),
                    Port(e[3][0], Operator[e[3][1]]) if e[3] else None,
                    e[4], e[5], e[6], e[7], e[8])
                for e in events]

        self._profile_store.add_events(Reference(instance_id), ev)
        return [ResponseType.SUCCESS.value]

    def _submit_snapshot(
            self, instance_id: str, snapshot: Dict[str, Any]) -> Any:
        """Handle a submit snapshot request.

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
        """
        snapshot_obj = SnapshotMetadata(**snapshot)
        instance = Reference(instance_id)
        self._snapshot_registry.register_snapshot(instance, snapshot_obj)
        return [ResponseType.SUCCESS.value]

    def _get_checkpoint_info(self, instance_id: str) -> Any:
        """Get checkpoint info for an instance

        Args:
            instance: The instance whose checkpoint info to get

        Returns:
            A list containing the following values on success:

            status (ResponseType): SUCCESS
            wallclock_reference_time (float): Unix timestamp (in UTC) indicating
                wallclock time of the start of the workflow.
            checkpoints (dict): Dictionary encoding a ymmsl.Checkpoints object.
            resume_path (Optional[str]): Checkpoint filename to resume from.
            snapshot_directory (Optional[str]): Directory to store instance
                snapshots.
        """
        instance = Reference(instance_id)
        resume = None
        if instance in self._configuration.resume:
            resume = str(self._configuration.resume[instance])

        snapshot_directory = None
        if self._run_dir is not None:
            snapshot_directory = str(self._run_dir.snapshot_dir(instance))

        return [ResponseType.SUCCESS.value,
                time.monotonic() - self._reference_time,
                encode_checkpoints(self._configuration.checkpoints),
                resume,
                snapshot_directory]

    def _waiting_for_receive(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]) -> Any:
        """Indicate that the instance is waiting to receive a message.

        Args:
            instance_id: The instance that is waiting
            port_name: Port name that the instance is waiting for
            slot: Slot that the instance is waiting for
        """
        self._deadlock_detector.waiting_for_receive(
                instance_id, peer_instance_id, port_name, slot)
        return [ResponseType.SUCCESS.value]

    def _waiting_for_receive_done(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]) -> Any:
        """Indicate that the instance is done waiting to receive a message.

        Args:
            instance_id: The instance that is waiting
            port_name: Port name that the instance is waiting for
            slot: Slot that the instance is waiting for
        """
        self._deadlock_detector.waiting_for_receive_done(
                instance_id, peer_instance_id, port_name, slot)
        return [ResponseType.SUCCESS.value]

    def _is_deadlocked(self, instance_id: str) -> Any:
        """Check if the provided instance is part of a detected deadlock.
        """
        result = self._deadlock_detector.is_deadlocked(instance_id)
        return [ResponseType.SUCCESS.value, result]


class MMPServer:
    """The MUSCLE Manager Protocol server.

    This class accepts connections from the instances comprising
    the multiscale model to be executed, and services them using an
    MMPRequestHandler.
    """
    def __init__(
            self,
            logger: Logger,
            profile_store: ProfileStore,
            configuration: PartialConfiguration,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore,
            snapshot_registry: SnapshotRegistry,
            deadlock_detector: DeadlockDetector,
            run_dir: Optional[RunDir]
            ) -> None:
        """Create an MMPServer.

        This starts a TCP Transport server and connects it to an
        MMPRequestHandler, which uses the given components to service
        the requests. By default, we listen on port 9000, unless it's
        not available in which case we use a random other one.

        Args:
            logger: Logger to send log messages to
            profile_store: ProfileStore to store profile data in
            configuration: Configuration component to get settings, checkpoints
                and resumes from
            instance_registry: To register instances with and get
                peer locations from
            topology_store: To get peers and conduits from
            snapshot_registry: To register snapshots with
            run_dir: To save snapshots to
        """
        self._handler = MMPRequestHandler(
                logger, profile_store, configuration, instance_registry,
                topology_store, snapshot_registry, deadlock_detector, run_dir)
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
