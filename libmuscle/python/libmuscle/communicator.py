from enum import IntEnum
import msgpack
from typing import Any, Dict, List, Optional, Tuple, Union, cast
from ymmsl import (ComputeElementDecl, Conduit, Identifier, Operator, Port,
                   Reference)

from libmuscle.configuration import Configuration
from libmuscle.configuration_store import ConfigurationStore
from libmuscle.mcp.message import Message as MCPMessage
from libmuscle.mcp.client import Client as MCPClient
from libmuscle.mcp.server import Server as MCPServer
from libmuscle.mcp.type_registry import client_types, server_types
from libmuscle.outbox import Outbox
from libmuscle.post_office import PostOffice


Message = Any


class Endpoint:
    """Place that a message is sent from and to.

    In the model description, we have kernels with ports connected by
    conduits. However, these kernels may be replicated, in which case
    there are many instances of them at run time. Thus, at run time
    there also need to be many conduit instances to connect the many
    kernel instances.

    A conduit always connects a port on a kernel to another port on
    another kernel. A conduit instance connects an endpoint to another
    endpoint. An endpoint has the name of a kernel, its index, the name
    of a port on that kernel, and a *slot*. The kernel and port name
    of a sender or receiver of a conduit instance come from the
    corresponding conduit.

    When a kernel is instantiated multiple times, the instances each
    have a unique index, which is a list of integers, to distinguish
    them from each other. Since a conduit instance connects kernel
    instances, each side will have an index to supply to the endpoint.
    The slot is a list of integers, like the index, and is passed when
    sending or receiving a message, and gives additional information
    on where to send the message.

    For example, assume a single kernel named ``abc`` with port ``p1``
    which is connected to a port ``p2`` on kernel ``def`` by a conduit,
    and of kernel ``def`` there are 10 instances. A message sent by
    ``abc`` on ``p1`` to the fourth instance of ``def`` port ``p2`` is
    sent from an endpoint with kernel ``abc``, index ``[]``, port
    ``p1`` and slot ``[3]``, and received on an endpoint with kernel
    ``def``, index ``[3]``, port ``p2`` and slot ``[]``.

    Conduit instances are never actually created in the code, but
    Endpoints are.
    """
    def __init__(self, kernel: Reference, index: List[int], port: Identifier,
                 slot: List[int]) -> None:
        """Create an Endpoint

        Note: kernel is a Reference, not an Identifier, because it may
        have namespace parts.

        Args:
            kernel: Name of an instance's kernel.
            index: Index of the kernel instance.
            port: Name of the port used.
            slot: Slot on which to send or receive.
        """
        self.kernel = kernel  # type: Reference
        self.index = index    # type: List[int]
        self.port = port      # type: Identifier
        self.slot = slot      # type: List[int]

    def ref(self) -> Reference:
        """Express as Reference.

        This yields a valid Reference of the form
        kernel[index].port[slot], with index and port omitted if they
        are zero-length.

        Returns:
            A Reference to this Endpoint.
        """
        ret = self.kernel
        if self.index:
            ret += self.index
        ret += self.port
        if self.slot:
            ret += self.slot
        return ret

    def __str__(self) -> str:
        """Convert to string.

        Returns this Endpoint as the string for of a Reference to it.
        See :meth:ref().

        Returns:
            The string representation of this Endpoint.
        """
        return str(self.ref())

    def instance(self) -> Reference:
        """Get a Reference to the instance this endpoint is on.
        """
        ret = self.kernel
        if self.index:
            ret += self.index
        return ret


class ExtTypeId(IntEnum):
    """MessagePack extension type ids.

    MessagePack lets you define your own types as an extension to the
    built-in ones. These are distinguished by a number from 0 to 127.
    This class is our registry of extension type ids.
    """
    CONFIGURATION = 0


class Communicator(PostOffice):
    """Communication engine for MUSCLE 3.

    This class is the mailroom for a kernel that uses MUSCLE 3. It
    manages the sending and receiving of messages, although it
    leaves the actual data transmission to various protocol-specific
    servers and clients.
    """
    def __init__(self, instance: Reference) -> None:
        """Create a Communicator.

        The instance reference must start with one or more Identifiers,
        giving the kernel id, followed by one or more integers which
        specify the instance index.

        Args:
            instance: The kernel instance this is the Communicator for.
        """
        self.__kernel, self.__index = self.__split_instance(instance)

        self.__servers = list()  # type: List[MCPServer]

        # indexed by remote instance id
        self.__clients = dict()  # type: Dict[Reference, MCPClient]

        # peer port ids, indexed by local kernel.port id
        self.__peers = dict()  # type: Dict[Reference, Reference]

        # indexed by receiving endpoint id
        self.__outboxes = dict()  # type: Dict[Reference, Outbox]

        for server_type in server_types:
            self.__servers.append(server_type(self))

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
        for conduit in conduits:
            if str(conduit.sending_compute_element()) == str(self.__kernel):
                # we send on the port this conduit attaches to
                self.__peers[conduit.sender] = conduit.receiver
            if str(conduit.receiving_compute_element()) == str(self.__kernel):
                # we receive on the port this conduit attaches to
                self.__peers[conduit.receiver] = conduit.sender

        self.__peer_dims = peer_dims    # indexed by kernel id
        self.__peer_locations = peer_locations  # indexed by instance id

    def send_message(
            self, port_name: str, message: Union[bytes, Message],
            overlay: Configuration, slot: Union[int, List[int]]=[]
            ) -> None:
        """Send a message and parameters to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        This function should not be used in submodels. It is intended
        for use by special compute elements that are ensemble-aware and
        either generate overlay parameter sets or pass them on.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            overlay: A parameter overlay to piggy-back onto the message.
            slot: The slot to send the message on, if any.
        """
        # note that slot is read-only, so the empty list default is fine
        if isinstance(slot, int):
            slot = [slot]

        # determine the sender
        try:
            snd_port = Identifier(port_name)
        except ValueError as e:
            raise ValueError('{} is not a valid port name: {}'.format(
                port_name, e))

        snd_endpoint = Endpoint(self.__kernel, self.__index, snd_port, slot)

        # balance the indexes and determine the receiver
        snd_port_full = self.__kernel + snd_port
        recv_kernel, recv_port = self.__split_peer(snd_port_full)

        total_index = self.__index + slot
        recv_dim = len(self.__peer_dims[recv_kernel])
        recv_index = total_index[0:recv_dim]
        recv_slot = total_index[recv_dim:]

        recv_endpoint = Endpoint(recv_kernel, recv_index, recv_port,
                                 recv_slot)

        # encode overlay
        packed_overlay = msgpack.packb(overlay.as_plain_dict(),
                                       use_bin_type=True)

        # encode message
        if isinstance(message, bytes):
            packed_message = message
        else:
            if isinstance(message, Configuration):
                data = msgpack.packb(message.as_plain_dict())
                ext_data = msgpack.ExtType(ExtTypeId.CONFIGURATION, data)
                packed_message = msgpack.packb(ext_data, use_bin_type=True)
            else:
                packed_message = msgpack.packb(message, use_bin_type=True)

        # deposit
        mcp_message = MCPMessage(snd_endpoint.ref(), recv_endpoint.ref(),
                                 packed_overlay, packed_message)
        self.__ensure_outbox_exists(recv_endpoint)
        self.__outboxes[recv_endpoint.ref()].deposit(mcp_message)

    def receive_message(self, port_name: str, decode: bool,
                        slot: Union[int, List[int]]=[]
                        ) -> Tuple[Message, Configuration]:
        """Receive a message and attached parameter overlay.

        This function should not be used in submodels. It is intended
        for use by special compute elements that are ensemble-aware and
        have to pass on overlay parameter sets explicitly.

        Receiving is a blocking operaton. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            decode: Whether to MsgPack-decode the message (True) or
                    return raw bytes() (False).
            slot: The slot to receive the message on, if any.

        Returns:
            The received message, decoded from MsgPack if decode is
            True and otherwise as a raw bytes object, and a
            Configuration holding the parameter overlay.
        """
        # note that slot is read-only, so the empty list default is fine
        if isinstance(slot, int):
            slot = [slot]

        recv_endpoint = self.__get_receiver(port_name, slot)
        snd_endpoint = self.__get_sender(recv_endpoint.port, slot)
        client = self.__get_client(snd_endpoint.instance())
        mcp_message = client.receive(recv_endpoint.ref())

        overlay_config = Configuration.from_plain_dict(msgpack.unpackb(
            mcp_message.parameter_overlay, raw=False))

        return self.__extract_object(mcp_message, decode), overlay_config

    def get_message(self, receiver: Reference) -> MCPMessage:
        """Get a message from a receiver's outbox.

        Used by servers to get messages that have been sent to another
        instance.

        Args:
            receiver: The receiver of the message, a reference to an
                    instance.
        """

        return self.__outboxes[receiver].retrieve()

    def __split_instance(self, instance: Reference
                         ) -> Tuple[Reference, List[int]]:
        """Split instance id into a kernel reference and an index.

        This assumes a valid instance id consisting of an optional
        sequence of namespaces, followed by the kernel identifier,
        followed by an optional index list, and splits it into the
        namespaced kernel identifier, and the index list.

        Args:
            instance: The instance we're the Communicator for.

        Returns:
            A kernel reference and index list.
        """
        i = 0
        while i < len(instance) and isinstance(instance[i], Identifier):
            i += 1
        kernel = instance[:i]

        index = list()  # type: List[int]
        while i < len(instance) and isinstance(instance[i], int):
            index.append(cast(int, instance[i]))
            i += 1

        return kernel, index

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
            for location in self.__peer_locations[instance]:
                if ClientType.can_connect_to(location):
                    client = cast(MCPClient, ClientType(location))
                    self.__clients[instance] = client
                    return client
        raise RuntimeError('Could not find a matching protocol for {}'.format(
                instance))

    def __ensure_outbox_exists(self, receiver: Endpoint) -> None:
        """Ensure that an outbox exists.

        Outboxes are created dynamically, the first time a message is
        sent to a receiver. This function checks that an outbox exists
        for a receiver, and if not, creates one.

        Args:
            receiver: The receiver that should have an outbox.
        """
        # TODO: get lock
        if receiver.ref() not in self.__outboxes:
            self.__outboxes[receiver.ref()] = Outbox()

    def __split_peer(self, full_port: Reference
                     ) -> Tuple[Reference, Identifier]:
        if full_port not in self.__peers:
            raise ValueError('Port {} does not exist or is not connected,'
                             ' please check the name and your conduit'
                             ' definitions.'.format(full_port))
        peer = self.__peers[full_port]
        return peer[:-1], cast(Identifier, peer[-1])

    def __get_receiver(self, port_name: str, slot: List[int]) -> Endpoint:
        """Determines the receiving endpoint for receiving a message.

        Args:
            port_name: Name of the port to receive on.
            slot: Slot to receive on.
        """
        try:
            recv_port = Identifier(port_name)
        except ValueError as e:
            raise ValueError('{} is not a valid port name: {}'.format(
                port_name, e))

        return Endpoint(self.__kernel, self.__index, recv_port, slot)

    def __get_sender(self, recv_port: Identifier, slot: List[int]) -> Endpoint:
        """Determine the sending endpoint for receiving a message.

        Args:
            recv_port: The receiving port.
            slot: The slot to receive on.

        Returns:
            The sending endpoint.
        """
        recv_port_full = self.__kernel + recv_port
        snd_kernel, snd_port = self.__split_peer(recv_port_full)

        total_index = self.__index + slot
        snd_dim = len(self.__peer_dims[snd_kernel])
        snd_index = total_index[0:snd_dim]
        snd_slot = total_index[snd_dim:]
        return Endpoint(snd_kernel, snd_index, snd_port, snd_slot)

    def __extract_object(self, mcp_message: MCPMessage, decode: bool
                         ) -> Message:
        """Extract object from a received message.

        Args:
            mcp_message: The received message.
            decode: Whether to decode, or return the raw data bytes.

        Returns:
            The object that was received.
        """

        if decode:
            data = msgpack.unpackb(mcp_message.data, raw=False)
            if isinstance(data, msgpack.ExtType):
                if data.code == ExtTypeId.CONFIGURATION:
                    plain_dict = msgpack.unpackb(data.data, raw=False)
                    return Configuration.from_plain_dict(plain_dict)
            return msgpack.unpackb(mcp_message.data, raw=False)
        else:
            return mcp_message.data
