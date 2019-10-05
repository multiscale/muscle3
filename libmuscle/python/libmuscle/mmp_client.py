from random import uniform
from time import perf_counter, sleep
from typing import Dict, Iterable, List, Tuple

import grpc
from ymmsl import Conduit, Port, Reference, Settings

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp
import muscle_manager_protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc

from libmuscle.port import port_to_grpc
from libmuscle.profiling import ProfileEvent
from libmuscle.logging import LogMessage


CONNECTION_TIMEOUT = 300
PEER_TIMEOUT = 600
PEER_INTERVAL_MIN = 5.0
PEER_INTERVAL_MAX = 10.0


def conduit_from_grpc(conduit: mmp.Conduit) -> Conduit:
    """Converts a Conduit from grpc to ymmsl.

    Args:
        conduit: A conduit.

    Returns:
        The same conduit, as ymmsl.Conduit.
    """
    return Conduit(conduit.sender, conduit.receiver)


class MMPClient():
    """The client for the MUSCLE Manager Protocol.

    This class connects to the Manager and communicates with it on \
    behalf of the rest of libmuscle.

    It manages the connection, and converts between our native types \
    and the gRPC generated types.
    """
    def __init__(self, location: str) -> None:
        """Create an MMPClient.

        Args:
            location: A connection string of the form hostname:port
        """
        channel = grpc.insecure_channel(location)
        ready = grpc.channel_ready_future(channel)
        try:
            ready.result(timeout=CONNECTION_TIMEOUT)
        except grpc.FutureTimeoutError:
            ready.cancel()
            channel.close()
            raise RuntimeError('Failed to connect to the MUSCLE manager')

        self.__client = mmp_grpc.MuscleManagerStub(channel)

    def submit_log_message(self, message: LogMessage) -> None:
        """Send a log message to the manager.

        Args:
            message: The message to send.
        """
        self.__client.SubmitLogMessage(message.to_grpc())

    def submit_profile_events(self, events: Iterable[ProfileEvent]) -> None:
        """Sends profiling events to the manager.

        Args:
            events: The events to send.
        """
        self.__client.SubmitProfileEvents(mmp.Profile(events=[
            e.to_grpc() for e in events]))

    def get_settings(self) -> Settings:
        """Get the central settings from the manager.

        Returns:
            The requested settings.
        """
        LLF = mmp.SETTING_VALUE_TYPE_LIST_LIST_FLOAT
        result = self.__client.RequestSettings(mmp.SettingsRequest())
        settings = Settings()
        for setting in result.setting_values:
            if setting.value_type == mmp.SETTING_VALUE_TYPE_STRING:
                settings[setting.name] = setting.value_string
            elif setting.value_type == mmp.SETTING_VALUE_TYPE_INT:
                settings[setting.name] = setting.value_int
            elif setting.value_type == mmp.SETTING_VALUE_TYPE_FLOAT:
                settings[setting.name] = setting.value_float
            elif setting.value_type == mmp.SETTING_VALUE_TYPE_BOOL:
                settings[setting.name] = setting.value_bool
            elif setting.value_type == mmp.SETTING_VALUE_TYPE_LIST_FLOAT:
                settings[setting.name] = list(
                        setting.value_list_float.values)
            elif setting.value_type == LLF:
                rows = list()   # type: List[List[float]]
                for mmp_row in setting.value_list_list_float.values:
                    rows.append(list(mmp_row.values))
                settings[setting.name] = rows
        return settings

    def register_instance(self, name: Reference, locations: List[str],
                          ports: List[Port]) -> None:
        """Register a compute element instance with the manager.

        Args:
            name: Name of the instance in the simulation.
            locations: List of places where the instance can be
                    reached.
            ports: List of ports of this instance.
        """
        grpc_ports = map(port_to_grpc, ports)
        request = mmp.RegistrationRequest(
                instance_name=str(name),
                network_locations=locations,
                ports=grpc_ports)
        self.__client.RegisterInstance(request)

    def request_peers(self, name: Reference
                      ) -> Tuple[List[Conduit],
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
        request = mmp.PeerRequest(instance_name=str(name))
        result = self.__client.RequestPeers(request)
        while (result.status == mmp.RESULT_STATUS_PENDING and
               perf_counter() < start_time + PEER_TIMEOUT and
               sleep_time < PEER_INTERVAL_MIN):
            sleep(sleep_time)
            result = self.__client.RequestPeers(request)
            sleep_time *= 1.5

        while (result.status == mmp.RESULT_STATUS_PENDING and
               perf_counter() < start_time + PEER_TIMEOUT):
            sleep(uniform(PEER_INTERVAL_MIN, PEER_INTERVAL_MAX))
            result = self.__client.RequestPeers(request)

        if result.status == mmp.RESULT_STATUS_PENDING:
            raise RuntimeError('Timeout waiting for peers to appear')

        if result.status == mmp.RESULT_STATUS_ERROR:
            raise RuntimeError('Error getting peers from manager: {}'.format(
                    result.error_message))

        conduits = list(map(conduit_from_grpc, result.conduits))

        peer_dimensions = dict()
        for peer_dimension in result.peer_dimensions:
            peer_dimensions[peer_dimension.peer_name] = \
                    peer_dimension.dimensions

        peer_locations = dict()
        for peer_location in result.peer_locations:
            peer_locations[peer_location.instance_name] = \
                    peer_location.locations

        return conduits, peer_dimensions, peer_locations

    def deregister_instance(self, name: Reference) -> None:
        """Deregister a compute element instance with the manager.

        Args:
            name: Name of the instance in the simulation.
        """
        request = mmp.DeregistrationRequest(
                instance_name=str(name))
        self.__client.DeregisterInstance(request)
