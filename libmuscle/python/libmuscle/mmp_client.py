from random import uniform
from time import perf_counter, sleep
from typing import Any, Dict, Iterable, List, Tuple

import msgpack
from ymmsl import Conduit, Operator, Port, Reference, Settings

from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.profiling import ProfileEvent
from libmuscle.logging import LogMessage


CONNECTION_TIMEOUT = 300
PEER_TIMEOUT = 600
PEER_INTERVAL_MIN = 5.0
PEER_INTERVAL_MAX = 10.0


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
    encoded_port = encode_port(event.port) if event.port else None
    return [
            str(event.instance_id),
            event.start_time.seconds, event.stop_time.seconds,
            event.event_type.value,
            encoded_port, event.port_length, event.slot,
            event.message_size]


class MMPClient():
    """The client for the MUSCLE Manager Protocol.

    This class connects to the Manager and communicates with it on
    behalf of the rest of libmuscle.

    It manages the connection, and converts between our native types
    and the gRPC generated types.
    """
    def __init__(self, location: str) -> None:
        """Create an MMPClient

        Args:
            location: A connection string of the form hostname:port
        """
        self._transport_client = TcpTransportClient(location)

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
                [encode_profile_event(e) for e in events]]
        self._call_manager(request)

    def get_settings(self) -> Settings:
        """Get the central settings from the manager.

        Returns:
            The requested settings.
        """
        request = [RequestType.GET_SETTINGS.value]
        response = self._call_manager(request)
        return Settings(response[1])

    def register_instance(self, name: Reference, locations: List[str],
                          ports: List[Port]) -> None:
        """Register a component instance with the manager.

        Args:
            name: Name of the instance in the simulation.
            locations: List of places where the instance can be
                    reached.
            ports: List of ports of this instance.
        """
        request = [
                RequestType.REGISTER_INSTANCE.value,
                str(name), locations,
                [encode_port(p) for p in ports]]
        response = self._call_manager(request)
        if len(response) > 1:
            raise RuntimeError(
                    f'Error registering instance: {response[1]}')

    def request_peers(
            self, name: Reference) -> Tuple[
                    List[Conduit],
                    Dict[Reference, List[int]],
                    Dict[Reference, List[str]]]:
        """Request connection information about peers.

        This will repeat the request at an exponentially increasing
        query interval at first, until it reaches the interval
        specified by PEER_INTERVAL_MIN and PEER_INTERVAL_MAX. From
        there on, intervals are drawn randomly from that range.

        Args:
            name: Name of the current instance.

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

        request = [RequestType.GET_PEERS.value, str(name)]
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

    def deregister_instance(self, name: Reference) -> None:
        """Deregister a component instance with the manager.

        Args:
            name: Name of the instance in the simulation.
        """
        request = [RequestType.DEREGISTER_INSTANCE.value, str(name)]
        response = self._call_manager(request)

        if response[0] == ResponseType.ERROR.value:
            raise RuntimeError('Error deregistering instance: {}'.format(
                    response[1]))

    def _call_manager(self, request: Any) -> Any:
        """Call the manager and do en/decoding.

        Args:
            request: The request to encode and send

        Returns:
            The decoded response
        """
        encoded_request = msgpack.packb(request, use_bin_type=True)
        response = self._transport_client.call(encoded_request)
        return msgpack.unpackb(response, raw=False)
