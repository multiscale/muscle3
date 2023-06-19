import logging
from typing import Any, Dict, List, Optional, Tuple, cast
from ymmsl import Conduit, Identifier, Operator, Reference, Settings

from libmuscle.endpoint import Endpoint
from libmuscle.mpp_message import ClosePort, MPPMessage
from libmuscle.mpp_client import MPPClient
from libmuscle.mcp.tcp_util import SocketClosed
from libmuscle.mcp.transport_server import TransportServer
from libmuscle.mcp.type_registry import transport_server_types
from libmuscle.peer_manager import PeerManager
from libmuscle.post_office import PostOffice
from libmuscle.port import Port
from libmuscle.profiler import Profiler
from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)


_logger = logging.getLogger(__name__)


MessageObject = Any


class Message:
    """A message to be sent or received.

    This class describes a message to be sent or that has been
    received.

    Attributes:
        timestamp (float): Simulation time for which this data is valid.
        next_timestamp (Optional[float]): Simulation time for the next
                message to be transmitted through this port.
        data (MessageObject): An object to send or that was received.
        settings (Settings): Overlay settings to send or that was
                received.
    """
    # Note: This is for communication with the user, it's not what
    # actually goes out on the wire, see libmuscle.mcp.Message for that.
    def __init__(self, timestamp: float, next_timestamp: Optional[float] = None,
                 data: MessageObject = None,
                 settings: Optional[Settings] = None
                 ) -> None:
        """Create a Message.

        Args:
            timestamp: Simulation time for which this data is valid.
            next_timestamp: Simulation time for the next message to be
                    transmitted through this port.
            data: An object to send or that was received.
            settings: Overlay settings to send or that were received.
        """
        # make sure timestamp and next_timestamp are floats
        timestamp = float(timestamp)
        if next_timestamp is not None:
            next_timestamp = float(next_timestamp)

        self.timestamp = timestamp
        self.next_timestamp = next_timestamp
        self.data = data
        self.settings = settings


class Communicator:
    """Communication engine for MUSCLE3.

    This class is the mailroom for a kernel that uses MUSCLE3. It
    manages the sending and receiving of messages, although it
    leaves the actual data transmission to various protocol-specific
    servers and clients.
    """
    def __init__(self, kernel: Reference, index: List[int],
                 declared_ports: Optional[Dict[Operator, List[str]]],
                 profiler: Profiler) -> None:
        """Create a Communicator.

        The instance reference must start with one or more Identifiers,
        giving the kernel id, followed by one or more integers which
        specify the instance index.

        Args:
            kernel: The kernel this is the Communicator for.
            index: The index for this instance.
            declared_ports: The declared ports for this instance
            profiler: The profiler to use for recording sends and
                    receives.
        """
        self._kernel = kernel
        self._index = index
        self._declared_ports = declared_ports
        self._post_office = PostOffice()
        self._profiler = profiler

        self._servers: List[TransportServer] = []

        # indexed by remote instance id
        self._clients: Dict[Reference, MPPClient] = {}

        for server_type in transport_server_types:
            server = server_type(self._post_office)
            self._servers.append(server)

        self._ports: Dict[str, Port] = {}

    def get_locations(self) -> List[str]:
        """Returns a list of locations that we can be reached at.

        These locations are of the form 'protocol:location', where
        the protocol name does not contain a colon and location may
        be an arbitrary string.

        Returns:
            A list of strings describing network locations.
        """
        return [server.get_location() for server in self._servers]

    def connect(self, conduits: List[Conduit],
                peer_dims: Dict[Reference, List[int]],
                peer_locations: Dict[Reference, List[str]]) -> None:
        """Connect this Communicator to its peers.

        This is the second stage in the simulation wiring process.

        Peers here are instances, and peer_dims and peer_locations are
        indexed by a Reference to an instance. Instance sets are
        multi-dimensional arrays with sizes given by peer_dims.

        Args:
            conduits: A list of conduits attached to this component,
                    as received from the manager.
            peer_dims: For each peer we share a conduit with, the
                    dimensions of the instance set.
            peer_locations: A list of locations for each peer instance
                    we share a conduit with.
        """
        self._peer_manager = PeerManager(
                self._kernel, self._index, conduits, peer_dims,
                peer_locations)

        if self._declared_ports is not None:
            self._ports = self.__ports_from_declared()
        else:
            self._ports = self.__ports_from_conduits(conduits)

        self._muscle_settings_in = self.__settings_in_port(conduits)

    def settings_in_connected(self) -> bool:
        """Returns True iff muscle_settings_in is connected.
        """
        return self._muscle_settings_in.is_connected()

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports this Communicator has.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        result: Dict[Operator, List[str]] = {}
        for port_name, port in self._ports.items():
            if port.operator not in result:
                result[port.operator] = list()
            result[port.operator].append(port_name)
        return result

    def port_exists(self, port_name: str) -> bool:
        """Returns whether a port with the given name exists.

        Args:
            port_name: Port name to check.
        """
        return port_name in self._ports

    def get_port(self, port_name: str) -> Port:
        """Returns a Port object describing a port with the given name.

        Args:
            port: The port to retrieve.
        """
        return self._ports[port_name]

    def send_message(
            self, port_name: str, message: Message,
            slot: Optional[int] = None,
            checkpoints_considered_until: float = float('-inf')) -> None:
        """Send a message and settings to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
            checkpoints_considered_until: When we last checked if we
                should save a snapshot (wallclock time).
        """
        if slot is None:
            _logger.debug('Sending message on {}'.format(port_name))
            slot_list: List[int] = []
        else:
            _logger.debug('Sending message on {}[{}]'.format(port_name, slot))
            slot_list = [slot]
            slot_length = self._ports[port_name].get_length()
            if slot_length <= slot:
                raise RuntimeError(('Slot out of bounds. You are sending on'
                                    ' slot {} of port "{}", which is of length'
                                    ' {}, so that slot does not exist'
                                    ).format(slot, port_name, slot_length))

        snd_endpoint = self.__get_endpoint(port_name, slot_list)
        if not self._peer_manager.is_connected(snd_endpoint.port):
            # log sending on disconnected port
            return

        port = self._ports[port_name]
        profile_event = ProfileEvent(
                ProfileEventType.SEND, ProfileTimestamp(), None, port, None,
                slot, port.get_num_messages(slot), None, message.timestamp)

        recv_endpoints = self._peer_manager.get_peer_endpoints(
                snd_endpoint.port, slot_list)

        port_length = None
        if port.is_resizable():
            port_length = port.get_length()

        for recv_endpoint in recv_endpoints:
            mpp_message = MPPMessage(snd_endpoint.ref(), recv_endpoint.ref(),
                                     port_length,
                                     message.timestamp, message.next_timestamp,
                                     cast(Settings, message.settings),
                                     port.get_num_messages(slot),
                                     checkpoints_considered_until,
                                     message.data)
            encoded_message = mpp_message.encoded()
            self._post_office.deposit(recv_endpoint.ref(), encoded_message)

        port.increment_num_messages(slot)

        profile_event.stop()
        if port.is_vector():
            profile_event.port_length = port.get_length()
        profile_event.message_size = len(encoded_message)
        if not isinstance(message.data, ClosePort):
            self._profiler.record_event(profile_event)

    def receive_message(self, port_name: str, slot: Optional[int] = None,
                        default: Optional[Message] = None
                        ) -> Tuple[Message, float]:
        """Receive a message and attached settings overlay.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port is not connected, then the default value will be
        returned if one was given, exactly as it was given. If no
        default was given then a RuntimeError will be raised.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            slot: The slot to receive the message on, if any.
            default: A message to return if this port is not connected.

        Returns:
            The received message, with message.settings holding
            the settings overlay. The settings attribute is
            guaranteed to not be None. Secondly, the saved_until
            metadata field from the received message.

        Raises:
            RuntimeError: If no default was given and the port is not
                connected.
        """
        if slot is None:
            port_and_slot = port_name
            slot_list: List[int] = []
        else:
            port_and_slot = f"{port_name}[{slot}]"
            slot_list = [slot]
        _logger.debug('Waiting for message on {}'.format(port_and_slot))

        recv_endpoint = self.__get_endpoint(port_name, slot_list)

        if not self._peer_manager.is_connected(recv_endpoint.port):
            if default is None:
                raise RuntimeError(('Tried to receive on port "{}", which is'
                                    ' disconnected, and no default value was'
                                    ' given. Either specify a default, or'
                                    ' connect a sending component to this'
                                    ' port.').format(port_name))
            _logger.debug(
                    'No message received on {} as it is not connected'.format(
                        port_name))
            return default, float('-inf')

        if port_name in self._ports:
            port = self._ports[port_name]
        else:
            # it's muscle_settings_in here, because we check for unknown
            # user ports in Instance already, and we don't have any other
            # built-in automatic ports.
            port = self._muscle_settings_in

        receive_event = ProfileEvent(
                ProfileEventType.RECEIVE, ProfileTimestamp(), None, port, None,
                slot, port.get_num_messages())

        # peer_manager already checks that there is at most one snd_endpoint
        # connected to the port we receive on
        snd_endpoint = self._peer_manager.get_peer_endpoints(
                recv_endpoint.port, slot_list)[0]
        client = self.__get_client(snd_endpoint.instance())
        try:
            mpp_message_bytes, profile = client.receive(recv_endpoint.ref())
        except (ConnectionError, SocketClosed) as exc:
            raise RuntimeError(
                "Error while receiving a message: connection with peer"
                f" '{snd_endpoint.kernel}' was lost. Did the peer crash?"
            ) from exc

        recv_decode_event = ProfileEvent(
                ProfileEventType.RECEIVE_DECODE, ProfileTimestamp(), None,
                port, None, slot, port.get_num_messages(),
                len(mpp_message_bytes))
        mpp_message = MPPMessage.from_bytes(mpp_message_bytes)
        recv_decode_event.stop()

        if mpp_message.port_length is not None:
            if port.is_resizable():
                port.set_length(mpp_message.port_length)

        if isinstance(mpp_message.data, ClosePort):
            port.set_closed(slot)

        message = Message(
                mpp_message.timestamp, mpp_message.next_timestamp,
                mpp_message.data, mpp_message.settings_overlay)

        recv_wait_event = ProfileEvent(
                ProfileEventType.RECEIVE_WAIT, profile[0], profile[1], port,
                mpp_message.port_length, slot, port.get_num_messages(),
                len(mpp_message_bytes), message.timestamp)

        recv_xfer_event = ProfileEvent(
                ProfileEventType.RECEIVE_TRANSFER, profile[1], profile[2],
                port, mpp_message.port_length, slot, port.get_num_messages(),
                len(mpp_message_bytes), message.timestamp)

        recv_decode_event.message_timestamp = message.timestamp
        receive_event.message_timestamp = message.timestamp

        if port.is_vector():
            receive_event.port_length = port.get_length()
            recv_wait_event.port_length = port.get_length()
            recv_xfer_event.port_length = port.get_length()
            recv_decode_event.port_length = port.get_length()

        receive_event.message_size = len(mpp_message_bytes)

        if not isinstance(mpp_message.data, ClosePort):
            self._profiler.record_event(recv_wait_event)
            self._profiler.record_event(recv_xfer_event)
            self._profiler.record_event(recv_decode_event)
            self._profiler.record_event(receive_event)

        expected_message_number = port.get_num_messages(slot)
        if expected_message_number != mpp_message.message_number:
            if (expected_message_number - 1 == mpp_message.message_number and
                    port.is_resuming(slot)):
                _logger.debug(f'Discarding received message on {port_and_slot}'
                              ': resuming from weakly consistent snapshot')
                port.set_resumed(slot)
                return self.receive_message(port_name, slot, default)
            raise RuntimeError(f'Received message on {port_and_slot} with'
                               ' unexpected message number'
                               f' {mpp_message.message_number}. Was expecting'
                               f' {expected_message_number}. Are you resuming'
                               ' from an inconsistent snapshot?')
        port.increment_num_messages(slot)

        _logger.debug('Received message on {}'.format(port_and_slot))
        if isinstance(mpp_message.data, ClosePort):
            _logger.debug('Port {} is now closed'.format(port_and_slot))

        return message, mpp_message.saved_until

    def close_port(self, port_name: str, slot: Optional[int] = None
                   ) -> None:
        """Closes the given port.

        This signals to any connected instance that no more messages
        will be sent on this port, which it can use to decide whether
        to shut down or continue running.

        Args:
            port_name: The name of the port to close.
        """
        message = Message(float('inf'), None, ClosePort(), Settings())
        if slot is None:
            _logger.debug('Closing port {}'.format(port_name))
        else:
            _logger.debug('Closing port {}[{}]'.format(port_name, slot))
        self.send_message(port_name, message, slot)

    def shutdown(self) -> None:
        """Shuts down the Communicator, closing connections.
        """
        for client in self._clients.values():
            client.close()

        self._post_office.wait_for_receivers()

        for server in self._servers:
            server.close()

    def restore_message_counts(self, port_message_counts: Dict[str, List[int]]
                               ) -> None:
        """Restore message counts on all ports.
        """
        for port_name, num_messages in port_message_counts.items():
            if port_name == "muscle_settings_in":
                self._muscle_settings_in.restore_message_counts(num_messages)
            elif port_name in self._ports:
                self._ports[port_name].restore_message_counts(num_messages)
            else:
                raise RuntimeError(f'Unknown port {port_name} in snapshot.'
                                   ' Have your port definitions changed since'
                                   ' the snapshot was taken?')

    def get_message_counts(self) -> Dict[str, List[int]]:
        """Get message counts for all ports on the communicator.
        """
        port_message_counts = {port_name: port.get_message_counts()
                               for port_name, port in self._ports.items()}
        port_message_counts["muscle_settings_in"] = \
            self._muscle_settings_in.get_message_counts()
        return port_message_counts

    def __instance_id(self) -> Reference:
        """Returns our complete instance id.
        """
        return self._kernel + self._index

    def __ports_from_declared(self) -> Dict[str, Port]:
        """Derives port definitions from supplied declaration.
        """
        ports = dict()
        declared_ports = cast(Dict[Operator, List[str]], self._declared_ports)
        for operator, port_list in declared_ports.items():
            for port_desc in port_list:
                port_name, is_vector = self.__split_port_desc(port_desc)
                if port_name.startswith('muscle_'):
                    raise RuntimeError(('Port names starting with "muscle_"'
                                        ' are reserved for MUSCLE, please'
                                        ' rename port "{}"'.format(port_name)))
                port_id = Identifier(port_name)
                is_connected = self._peer_manager.is_connected(port_id)
                if is_connected:
                    peer_ports = self._peer_manager.get_peer_ports(port_id)
                    peer_port = peer_ports[0]
                    peer_ce = peer_port[:-1]
                    port_peer_dims = self._peer_manager.get_peer_dims(peer_ce)
                    for peer_port in peer_ports[1:]:
                        peer_ce = peer_port[:-1]
                        if port_peer_dims != self._peer_manager.get_peer_dims(
                                peer_ce):
                            port_strs = ', '.join(map(str, peer_ports))
                            raise RuntimeError(('Multicast port "{}" is'
                                                ' connected to peers with'
                                                ' different dimensions. All'
                                                ' peer components that this'
                                                ' port is connected to must'
                                                ' have the same multiplicity.'
                                                ' Connected to ports: {}.'
                                                ).format(port_name, port_strs))
                else:
                    port_peer_dims = []
                ports[port_name] = Port(
                        port_name, operator, is_vector, is_connected,
                        len(self._index), port_peer_dims)
        return ports

    def __ports_from_conduits(self, conduits: List[Conduit]
                              ) -> Dict[str, Port]:
        """Derives port definitions from conduits.

        Args:
            conduits: The list of conduits.
        """
        ports = dict()
        for conduit in conduits:
            if conduit.sending_component() == self._kernel:
                port_id = conduit.sending_port()
                operator = Operator.O_F
                port_peer_dims = self._peer_manager.get_peer_dims(
                        conduit.receiving_component())
            elif conduit.receiving_component() == self._kernel:
                port_id = conduit.receiving_port()
                operator = Operator.F_INIT
                port_peer_dims = self._peer_manager.get_peer_dims(
                        conduit.sending_component())
            else:
                continue

            ndims = max(0, len(port_peer_dims) - len(self._index))
            is_vector = (ndims == 1)
            is_connected = self._peer_manager.is_connected(port_id)
            if not str(port_id).startswith('muscle_'):
                ports[str(port_id)] = Port(
                        str(port_id), operator, is_vector, is_connected,
                        len(self._index), port_peer_dims)
        return ports

    def __settings_in_port(self, conduits: List[Conduit]) -> Port:
        """Creates a Port representing muscle_settings_in.

        Args:
            conduits: The list of conduits.
        """
        for conduit in conduits:
            if conduit.receiving_component() == self._kernel:
                port_id = conduit.receiving_port()
                if str(port_id) == 'muscle_settings_in':
                    return Port(str(port_id), Operator.F_INIT, False,
                                self._peer_manager.is_connected(port_id),
                                len(self._index),
                                self._peer_manager.get_peer_dims(
                                    conduit.sending_component()))
        return Port('muscle_settings_in', Operator.F_INIT, False, False,
                    len(self._index), [])

    def __get_client(self, instance: Reference) -> MPPClient:
        """Get or create a client to connect to the given instance.

        Args:
            instance: A reference to the instance to connect to.

        Returns:
            An existing or new MCP client.
        """
        if instance not in self._clients:
            locations = self._peer_manager.get_peer_locations(instance)
            _logger.info(f'Connecting to peer {instance} at {locations}')
            self._clients[instance] = MPPClient(locations)

        return self._clients[instance]

    def __get_endpoint(self, port_name: str, slot: List[int]) -> Endpoint:
        """Determines the endpoint on our side.

        Args:
            port_name: Name of the port to send or receive on.
            slot: Slot to send or receive on.
        """
        try:
            port = Identifier(port_name)
        except ValueError as e:
            raise ValueError('"{}" is not a valid port name: {}'.format(
                port_name, e))

        return Endpoint(self._kernel, self._index, port, slot)

    def __split_port_desc(self, port_desc: str) -> Tuple[str, bool]:
        """Split a port description into its name and dimensionality.

        Expects a port description of the form port_name or
        port_name[], and returns the port name and whether it is a
        vector port.

        Args:
            port_desc: A port description string, as above.
        """
        is_vector = False
        if port_desc.endswith('[]'):
            is_vector = True
            port_desc = port_desc[:-2]

        if port_desc.endswith('[]'):
            raise ValueError(('Port description "{}" is invalid: ports can'
                              ' have at most one dimension.').format(
                                  port_desc))

        return port_desc, is_vector
