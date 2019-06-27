from enum import IntEnum
import msgpack
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from ymmsl import Conduit, Identifier, Operator, Reference, Settings

from libmuscle.endpoint import Endpoint
from libmuscle.mcp.message import Message as MCPMessage
from libmuscle.mcp.client import Client as MCPClient
from libmuscle.mcp.server import Server as MCPServer, ServerNotSupported
from libmuscle.mcp.type_registry import client_types, server_types
from libmuscle.peer_manager import PeerManager
from libmuscle.post_office import PostOffice
from libmuscle.port import Port
from libmuscle.profiler import Profiler
from libmuscle.profiling import ProfileEvent, ProfileEventType


MessageObject = Any


class ExtTypeId(IntEnum):
    """MessagePack extension type ids.

    MessagePack lets you define your own types as an extension to the
    built-in ones. These are distinguished by a number from 0 to 127.
    This class is our registry of extension type ids.
    """
    CLOSE_PORT = 0
    SETTINGS = 1


class _ClosePort:
    """Sentinel value to send when closing a port.

    Sending an object of this class on a port/conduit conveys to the
    receiver the message that no further messages will be sent on this
    port during the simulation.

    All information is carried by the type, this has no attributes.
    """
    pass


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
    def __init__(self, timestamp: float, next_timestamp: Optional[float],
                 data: MessageObject,
                 settings: Optional[Settings]=None
                 ) -> None:
        """Create a Message.

        Args:
            timestamp: Simulation time for which this data is valid.
            next_timestamp: Simulation time for the next message to be
                    transmitted through this port.
            data: An object to send or that was received.
            settings: Overlay settings to send or that were received.
        """
        self.timestamp = timestamp
        self.next_timestamp = next_timestamp
        self.data = data
        self.settings = settings


class Communicator(PostOffice):
    """Communication engine for MUSCLE 3.

    This class is the mailroom for a kernel that uses MUSCLE 3. It
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
        super().__init__()

        self.__kernel = kernel
        self.__index = index
        self.__declared_ports = declared_ports
        self.__profiler = profiler

        self.__servers = list()  # type: List[MCPServer]

        # indexed by remote instance id
        self.__clients = dict()  # type: Dict[Reference, MCPClient]

        for server_type in server_types:
            try:
                server = server_type(self.__instance_id(), self)
                self.__servers.append(server)
            except ServerNotSupported:
                pass

        self.__ports = dict()   # type: Dict[str, Port]

    def get_locations(self) -> List[str]:
        """Returns a list of locations that we can be reached at.

        These locations are of the form 'protocol:location', where
        the protocol name does not contain a colon and location may
        be an arbitrary string.

        Returns:
            A list of strings describing network locations.
        """
        return [server.get_location() for server in self.__servers]

    def connect(self, conduits: List[Conduit],
                peer_dims: Dict[Reference, List[int]],
                peer_locations: Dict[Reference, List[str]]) -> None:
        """Connect this Communicator to its peers.

        This is the second stage in the simulation wiring process.

        Peers here are instances, and peer_dims and peer_locations are
        indexed by a Reference to an instance. Instance sets are
        multi-dimensional arrays with sizes given by peer_dims.

        Args:
            conduits: A list of conduits attached to this compute
                    element, as received from the manager.
            peer_dims: For each peer we share a conduit with, the
                    dimensions of the instance set.
            peer_locations: A list of locations for each peer instance
                    we share a conduit with.
        """
        self.__peer_manager = PeerManager(
                self.__kernel, self.__index, conduits, peer_dims,
                peer_locations)

        if self.__declared_ports is not None:
            self.__ports = self.__ports_from_declared()
        else:
            self.__ports = self.__ports_from_conduits(conduits)

        self.__muscle_settings_in = self.__parameters_in_port(conduits)

    def parameters_in_connected(self) -> bool:
        """Returns True iff muscle_settings_in is connected.
        """
        return self.__muscle_settings_in.is_connected()

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports this Communicator has.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        result = dict()     # type: Dict[Operator, List[str]]
        for port_name, port in self.__ports.items():
            if port.operator not in result:
                result[port.operator] = list()
            result[port.operator].append(port_name)
        return result

    def port_exists(self, port_name: str) -> bool:
        """Returns whether a port with the given name exists.

        Args:
            port_name: Port name to check.
        """
        return port_name in self.__ports

    def get_port(self, port_name: str) -> Port:
        """Returns a Port object describing a port with the given name.

        Args:
            port: The port to retrieve.
        """
        return self.__ports[port_name]

    def send_message(
            self, port_name: str, message: Message,
            slot: Optional[int]=None) -> None:
        """Send a message and parameters to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        if slot is None:
            slot_list = []  # type: List[int]
        else:
            slot_list = [slot]
            slot_length = self.__ports[port_name].get_length()
            if slot_length <= slot:
                raise RuntimeError(('Slot out of bounds. You are sending on'
                                    ' slot {} of port "{}", which is of length'
                                    ' {}, so that slot does not exist'
                                    ).format(slot, port_name, slot_length))

        snd_endpoint = self.__get_endpoint(port_name, slot_list)
        if not self.__peer_manager.is_connected(snd_endpoint.port):
            # log sending on disconnected port
            return

        port = self.__ports[port_name]
        profile_event = self.__profiler.start(ProfileEventType.SEND, port,
                                              None, slot, None)

        recv_endpoint = self.__peer_manager.get_peer_endpoint(
                snd_endpoint.port, slot_list)

        packed_overlay = self.__pack_object(
                cast(Settings, message.settings).as_ordered_dict())

        packed_message = self.__pack_object(message.data)

        port_length = None
        if self.__ports[port_name].is_resizable():
            port_length = self.__ports[port_name].get_length()

        mcp_message = MCPMessage(snd_endpoint.ref(), recv_endpoint.ref(),
                                 port_length,
                                 message.timestamp, message.next_timestamp,
                                 packed_overlay, packed_message)
        self._deposit(recv_endpoint.ref(), mcp_message)
        profile_event.stop()
        if port.is_vector():
            profile_event.port_length = port.get_length()
        profile_event.message_size = len(mcp_message.data)

    def receive_message(self, port_name: str, slot: Optional[int]=None,
                        default: Optional[Message]=None
                        ) -> Message:
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
            the parameter overlay. The settings attribute is
            guaranteed to not be None.

        Raises:
            RuntimeError: If no default was given and the port is not
                connected.
        """
        if slot is None:
            slot_list = []      # type: List[int]
        else:
            slot_list = [slot]

        recv_endpoint = self.__get_endpoint(port_name, slot_list)

        if not self.__peer_manager.is_connected(recv_endpoint.port):
            if default is None:
                raise RuntimeError(('Tried to receive on port "{}", which is'
                                    ' disconnected, and no default value was'
                                    ' given. Either specify a default, or'
                                    ' connect a sending component to this'
                                    ' port.').format(port_name))
            return default

        if port_name in self.__ports:
            port = self.__ports[port_name]
        else:
            # it's muscle_settings_in here, because we check for unknown
            # user ports in Instance already, and we don't have any other
            # built-in automatic ports.
            port = self.__muscle_settings_in

        profile_event = self.__profiler.start(ProfileEventType.RECEIVE, port,
                                              None, slot, None)

        snd_endpoint = self.__peer_manager.get_peer_endpoint(
                recv_endpoint.port, slot_list)
        client = self.__get_client(snd_endpoint.instance())
        mcp_message = client.receive(recv_endpoint.ref())

        overlay_settings = Settings(msgpack.unpackb(
            mcp_message.parameter_overlay, raw=False))

        if mcp_message.port_length is not None:
            if port.is_resizable():
                port.set_length(mcp_message.port_length)

        message = Message(
                mcp_message.timestamp, mcp_message.next_timestamp,
                self.__extract_object(mcp_message), overlay_settings)

        if isinstance(message.data, _ClosePort):
            port.set_closed(slot)

        profile_event.stop()
        if port.is_vector():
            profile_event.port_length = port.get_length()
        profile_event.message_size = len(mcp_message.data)

        return message

    def close_port(self, port_name: str, slot: Optional[int]=None
                   ) -> None:
        """Closes the given port.

        This signals to any connected instance that no more messages
        will be sent on this port, which it can use to decided whether
        to shut down or continue running.

        Args:
            port_name: The name of the port to close.
        """
        message = Message(float('inf'), None, _ClosePort(), Settings())
        self.send_message(port_name, message, slot)

    def shutdown(self) -> None:
        """Shuts down the Communicator, closing connections.
        """
        for client in self.__clients.values():
            client.close()
        for client_type in client_types:
            client_type.shutdown(self.__instance_id())

        self._wait_for_receivers()

        for server in self.__servers:
            server.close()

    def __instance_id(self) -> Reference:
        """Returns our complete instance id.
        """
        return self.__kernel + self.__index

    def __ports_from_declared(self) -> Dict[str, Port]:
        """Derives port definitions from supplied declaration.
        """
        ports = dict()
        declared_ports = cast(Dict[Operator, List[str]], self.__declared_ports)
        for operator, port_list in declared_ports.items():
            for port_desc in port_list:
                port_name, is_vector = self.__split_port_desc(port_desc)
                if port_name.startswith('muscle_'):
                    raise RuntimeError(('Port names starting with "muscle_"'
                                        ' are reserved for MUSCLE, please'
                                        ' rename port "{}"'.format(port_name)))
                is_connected = self.__peer_manager.is_connected(
                        Identifier(port_name))
                if is_connected:
                    port_ref = self.__kernel + Identifier(port_name)
                    peer_port = self.__peer_manager.get_peer_port(port_ref)
                    peer_ce = peer_port[:-1]
                    port_peer_dims = self.__peer_manager.get_peer_dims(peer_ce)
                else:
                    port_peer_dims = []
                ports[port_name] = Port(
                        port_name, operator, is_vector, is_connected,
                        len(self.__index), port_peer_dims)
        return ports

    def __ports_from_conduits(self, conduits: List[Conduit]
                              ) -> Dict[str, Port]:
        """Derives port definitions from conduits.

        Args:
            conduits: The list of conduits.
        """
        ports = dict()
        for conduit in conduits:
            if conduit.sending_compute_element() == self.__kernel:
                port_id = conduit.sending_port()
                operator = Operator.O_F
                port_peer_dims = self.__peer_manager.get_peer_dims(
                        conduit.receiving_compute_element())
            elif conduit.receiving_compute_element() == self.__kernel:
                port_id = conduit.receiving_port()
                operator = Operator.F_INIT
                port_peer_dims = self.__peer_manager.get_peer_dims(
                        conduit.sending_compute_element())
            ndims = max(0, len(port_peer_dims) - len(self.__index))
            is_vector = (ndims == 1)
            is_connected = self.__peer_manager.is_connected(port_id)
            if not str(port_id).startswith('muscle_'):
                ports[str(port_id)] = Port(
                        str(port_id), operator, is_vector, is_connected,
                        len(self.__index), port_peer_dims)
        return ports

    def __parameters_in_port(self, conduits: List[Conduit]) -> Port:
        """Creates a Port representing muscle_settings_in.

        Args:
            conduits: The list of conduits.
        """
        for conduit in conduits:
            if conduit.receiving_compute_element() == self.__kernel:
                port_id = conduit.receiving_port()
                if str(port_id) == 'muscle_settings_in':
                    return Port(str(port_id), Operator.F_INIT, False,
                                self.__peer_manager.is_connected(port_id),
                                len(self.__index),
                                self.__peer_manager.get_peer_dims(
                                    conduit.sending_compute_element()))
        return Port('muscle_settings_in', Operator.F_INIT, False, False,
                    len(self.__index), [])

    def __get_client(self, instance: Reference) -> MCPClient:
        """Get or create a client to connect to the given instance.

        Args:
            instance: A reference to the instance to connect to.

        Returns:
            An existing or new MCP client.
        """
        if instance in self.__clients:
            return self.__clients[instance]

        for ClientType in client_types:
            for location in self.__peer_manager.get_peer_locations(instance):
                if ClientType.can_connect_to(location):
                    client = ClientType(self.__instance_id(), location)
                    self.__clients[instance] = client
                    return client
        raise RuntimeError('Could not find a matching protocol for {}'.format(
                instance))

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

        return Endpoint(self.__kernel, self.__index, port, slot)

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

    def __extract_object(self, mcp_message: MCPMessage) -> MessageObject:
        """Extract object from a received message.

        Args:
            mcp_message: The received message.

        Returns:
            The object that was received.
        """
        data = msgpack.unpackb(mcp_message.data, raw=False)
        if isinstance(data, msgpack.ExtType):
            if data.code == ExtTypeId.CLOSE_PORT:
                return _ClosePort()
            elif data.code == ExtTypeId.SETTINGS:
                plain_dict = msgpack.unpackb(data.data, raw=False)
                return Settings(plain_dict)
        return msgpack.unpackb(mcp_message.data, raw=False)

    def __pack_object(self, obj: MessageObject) -> bytes:
        """MessagePack-encode an object for transmission.

        Args:
            obj: The object to pack.

        Returns:
            MessagePack-encoded bytes.
        """
        if isinstance(obj, _ClosePort):
            obj = msgpack.ExtType(ExtTypeId.CLOSE_PORT, bytes())
        elif isinstance(obj, Settings):
            data = msgpack.packb(obj.as_ordered_dict())
            obj = msgpack.ExtType(ExtTypeId.SETTINGS, data)
        packed_message = msgpack.packb(obj, use_bin_type=True)
        return cast(bytes, packed_message)
