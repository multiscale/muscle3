import dataclasses
from pathlib import Path
from random import uniform
from threading import Lock
from time import perf_counter, sleep
from typing import Any, Dict, Iterable, List, Optional, Tuple

import msgpack
from ymmsl import (
        Conduit, Operator, Port, Reference, Settings, Checkpoints,
        CheckpointRule, CheckpointRangeRule, CheckpointAtRule)

import libmuscle
from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.profiling import ProfileEvent
from libmuscle.logging import LogMessage
from libmuscle.snapshot import SnapshotMetadata


PEER_TIMEOUT = 600
PEER_INTERVAL_MIN = 5.0
PEER_INTERVAL_MAX = 10.0

_CheckpointInfoType = Tuple[
        float, Checkpoints, Optional[Path], Optional[Path]]


def encode_operator(op: Operator) -> str:
    """Convert an Operator to a MsgPack-compatible value."""
    return op.name


def encode_port(port: Port) -> List[str]:
    """Convert a Port to a MsgPack-compatible value."""
    return [str(port.name), encode_operator(port.operator)]


def encode_profile_event(event: ProfileEvent) -> Any:
    """Converts a ProfileEvent to a list.

    Args:
        event: A profile event

    Returns:
        A list with its attributes, for MMP serialisation.
    """
    if event.start_time is None or event.stop_time is None:
        raise RuntimeError(
                'Incomplete ProfileEvent sent. This is a bug, please'
                ' report it.')

    encoded_port = encode_port(event.port) if event.port else None
    return [
            event.event_type.value,
            event.start_time.nanoseconds, event.stop_time.nanoseconds,
            encoded_port, event.port_length, event.slot,
            event.message_number, event.message_size, event.message_timestamp]


def decode_checkpoint_rule(rule: Dict[str, Any]) -> CheckpointRule:
    """Decode a checkpoint rule from a MsgPack-compatible value."""
    if rule.keys() == {'at'}:
        return CheckpointAtRule(**rule)
    if rule.keys() == {'start', 'stop', 'every'}:
        return CheckpointRangeRule(**rule)
    raise ValueError(f'Cannot convert {rule} to a checkpoint rule.')


def decode_checkpoint_info(
        elapsed_time: float,
        checkpoints_dict: Dict[str, Any],
        resume: Optional[str],
        snapshot_dir: Optional[str]
        ) -> _CheckpointInfoType:
    """Decode checkpoint info from a MsgPack-compatible value.

    Args:
        elapsed_time: current elapsed time according to the manager
        checkpoints_dict: checkpoint definitions from the MsgPack
        resume: path to the snapshot we should resume from, if any
        snapshot_dir: path to the directory to store new snapshots in

    Returns:
        elapsed_time: current elapsed time according to the manager
        checkpoints: checkpoint configuration
        resume: path to the snapshot we should resume from, if any
        snapshot_dir: path to the directory to store new snapshots in
    """
    checkpoints = Checkpoints(
            at_end=checkpoints_dict["at_end"],
            wallclock_time=[decode_checkpoint_rule(rule)
                            for rule in checkpoints_dict["wallclock_time"]],
            simulation_time=[decode_checkpoint_rule(rule)
                             for rule in checkpoints_dict["simulation_time"]])
    resume_path = None if resume is None else Path(resume)
    snapshot_path = None if snapshot_dir is None else Path(snapshot_dir)
    return (elapsed_time, checkpoints, resume_path, snapshot_path)


class MMPClient():
    """The client for the MUSCLE Manager Protocol.

    This class connects to the Manager and communicates with it on
    behalf of the rest of libmuscle.

    It manages the connection, and converts between our native types
    and the gRPC generated types.

    Communication is protected by an internal lock, so this class can
    be called simultaneously from different threads.
    """
    def __init__(self, instance_id: Reference, location: str) -> None:
        """Create an MMPClient

        Args:
            location: A connection string of the form hostname:port
        """
        self._instance_id = instance_id
        self._transport_client = TcpTransportClient(location)
        self._mutex = Lock()

    def close(self) -> None:
        """Close the connection

        This closes the connection. After this no other member
        functions can be called.
        """
        self._transport_client.close()

    def submit_log_message(self, message: LogMessage) -> None:
        """Send a log message to the manager.

        Args:
            message: The message to send.
        """
        request = [
                RequestType.SUBMIT_LOG_MESSAGE.value,
                message.instance_id, message.timestamp.seconds,
                message.level.value, message.text]
        self._call_manager(request)

    def submit_profile_events(self, events: Iterable[ProfileEvent]) -> None:
        """Sends profiling events to the manager.

        Args:
            events: The events to send.
        """
        request = [
                RequestType.SUBMIT_PROFILE_EVENTS.value,
                str(self._instance_id),
                [encode_profile_event(e) for e in events]]
        self._call_manager(request)

    def submit_snapshot_metadata(
            self, snapshot_metadata: SnapshotMetadata) -> None:
        """Send snapshot metadata to the manager.

        Args:
            snapshot_metadata: Snapshot metadata to supply to the manager.
        """
        request = [
                RequestType.SUBMIT_SNAPSHOT.value,
                str(self._instance_id),
                dataclasses.asdict(snapshot_metadata)]
        self._call_manager(request)

    def get_settings(self) -> Settings:
        """Get the central settings from the manager.

        Returns:
            The requested settings.
        """
        request = [RequestType.GET_SETTINGS.value]
        response = self._call_manager(request)
        return Settings(response[1])

    def get_checkpoint_info(self) -> _CheckpointInfoType:
        """Get the checkpoint info from the manager.

        Returns:
            elapsed_time: current elapsed time
            checkpoints: checkpoint configuration
            resume: path to the resume snapshot
            snapshot_directory: path to store snapshots
        """
        request = [RequestType.GET_CHECKPOINT_INFO.value, str(self._instance_id)]
        response = self._call_manager(request)
        return decode_checkpoint_info(*response[1:])

    def register_instance(
            self, locations: List[str], ports: List[Port]) -> None:
        """Register a component instance with the manager.

        Args:
            locations: List of places where the instance can be
                    reached.
            ports: List of ports of this instance.
        """
        request = [
                RequestType.REGISTER_INSTANCE.value,
                str(self._instance_id), locations,
                [encode_port(p) for p in ports],
                libmuscle.__version__]
        response = self._call_manager(request)
        if response[0] == ResponseType.ERROR.value:
            raise RuntimeError(
                    f'Error registering instance: {response[1]}')

    def request_peers(self) -> Tuple[
            List[Conduit],
            Dict[Reference, List[int]],
            Dict[Reference, List[str]]]:
        """Request connection information about peers.

        This will repeat the request at an exponentially increasing
        query interval at first, until it reaches the interval
        specified by PEER_INTERVAL_MIN and PEER_INTERVAL_MAX. From
        there on, intervals are drawn randomly from that range.

        Returns:
            A tuple containing a list of conduits that this instance is
            attached to, a dictionary of peer dimensions, which is
            indexed by Reference to the peer kernel, and specifies how
            many instances of that kernel there are, and a dictionary
            of peer instance locations, indexed by Reference to a peer
            instance, and containing for each peer instance a list of
            network location strings at which it can be reached.
        """
        sleep_time = 0.1
        start_time = perf_counter()

        request = [RequestType.GET_PEERS.value, str(self._instance_id)]
        response = self._call_manager(request)

        while (response[0] == ResponseType.PENDING.value and
               perf_counter() < start_time + PEER_TIMEOUT and
               sleep_time < PEER_INTERVAL_MIN):
            sleep(sleep_time)
            response = self._call_manager(request)
            sleep_time *= 1.5

        while (response[0] == ResponseType.PENDING.value and
               perf_counter() < start_time + PEER_TIMEOUT):
            sleep(uniform(PEER_INTERVAL_MIN, PEER_INTERVAL_MAX))
            response = self._call_manager(request)

        if response[0] == ResponseType.PENDING.value:
            raise RuntimeError('Timeout waiting for peers to appear')

        if response[0] == ResponseType.ERROR.value:
            raise RuntimeError('Error getting peers from manager: {}'.format(
                    response[1]))

        conduits = [Conduit(snd, recv) for snd, recv in response[1]]

        peer_dimensions = {
                Reference(component): dims
                for component, dims in response[2].items()}

        peer_locations = {
                Reference(instance): locs
                for instance, locs in response[3].items()}

        return conduits, peer_dimensions, peer_locations

    def deregister_instance(self) -> None:
        """Deregister a component instance with the manager.
        """
        request = [
                RequestType.DEREGISTER_INSTANCE.value, str(self._instance_id)]
        response = self._call_manager(request)

        if response[0] == ResponseType.ERROR.value:
            raise RuntimeError('Error deregistering instance: {}'.format(
                    response[1]))

    def waiting_for_receive(
            self, peer_instance_id: Reference, port_name: str, slot: Optional[int]
            ) -> None:
        """Notify the manager that we're waiting to receive a message."""
        request = [
                RequestType.WAITING_FOR_RECEIVE.value,
                str(self._instance_id),
                str(peer_instance_id), port_name, slot]
        self._call_manager(request)

    def waiting_for_receive_done(
            self, peer_instance_id: Reference, port_name: str, slot: Optional[int]
            ) -> None:
        """Notify the manager that we're done waiting to receive a message."""
        request = [
                RequestType.WAITING_FOR_RECEIVE_DONE.value,
                str(self._instance_id),
                str(peer_instance_id), port_name, slot]
        self._call_manager(request)

    def is_deadlocked(self) -> bool:
        """Ask the manager if we're part of a deadlock."""
        request = [
                RequestType.IS_DEADLOCKED.value, str(self._instance_id)]
        response = self._call_manager(request)
        return bool(response[1])

    def _call_manager(self, request: Any) -> Any:
        """Call the manager and do en/decoding.

        Args:
            request: The request to encode and send

        Returns:
            The decoded response
        """
        with self._mutex:
            encoded_request = msgpack.packb(request, use_bin_type=True)
            response, _ = self._transport_client.call(encoded_request)
            return msgpack.unpackb(response, raw=False)
