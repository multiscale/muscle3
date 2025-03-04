import logging
from typing import Any, Dict, List, Optional, Tuple, cast
from ymmsl import Identifier, Reference, Settings

from libmuscle.endpoint import Endpoint
from libmuscle.mmp_client import MMPClient
from libmuscle.mpp_message import ClosePort, MPPMessage
from libmuscle.mpp_client import MPPClient
from libmuscle.mpp_server import MPPServer
from libmuscle.mcp.tcp_util import SocketClosed
from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.profiler import Profiler
from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)
from libmuscle.receive_timeout_handler import Deadlock, ReceiveTimeoutHandler


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
    def __init__(
            self, kernel: Reference, index: List[int],
            port_manager: PortManager, profiler: Profiler,
            manager: MMPClient) -> None:
        """Create a Communicator.

        The instance reference must start with one or more Identifiers,
        giving the kernel id, followed by one or more integers which
        specify the instance index.

        Args:
            kernel: The kernel this is the Communicator for.
            index: The index for this instance.
            port_manager: The PortManager to use.
            profiler: The profiler to use for recording sends and
                    receives.
        """
        self._kernel = kernel
        self._index = index
        self._port_manager = port_manager
        self._profiler = profiler
        self._manager = manager
        # Notify manager, by default, after 10 seconds waiting in receive_message()
        self._receive_timeout = 10.0

        self._server = MPPServer()

        # indexed by remote instance id
        self._clients: Dict[Reference, MPPClient] = {}

    def get_locations(self) -> List[str]:
        """Returns a list of locations that we can be reached at.

        These locations are of the form 'protocol:location', where
        the protocol name does not contain a colon and location may
        be an arbitrary string.

        Returns:
            A list of strings describing network locations.
        """
        return self._server.get_locations()

    def set_peer_info(self, peer_info: PeerInfo) -> None:
        """Inform this Communicator about its peers.

        This tells the Communicator about its peers, so that it can route
        messages accordingly.

        Args:
            peer_info: Information about the peers.
        """
        self._peer_info = peer_info

    def set_receive_timeout(self, receive_timeout: float) -> None:
        """Update the timeout after which the manager is notified that we are waiting
        for a message.

        Args:
            receive_timeout: Timeout (seconds). A negative number disables the deadlock
                notification mechanism.
        """
        self._receive_timeout = receive_timeout

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

        snd_endpoint = self.__get_endpoint(port_name, slot_list)
        if not self._port_manager.get_port(str(snd_endpoint.port)).is_connected():
            # log sending on disconnected port
            return

        port = self._port_manager.get_port(port_name)
        profile_event = ProfileEvent(
                ProfileEventType.SEND, ProfileTimestamp(), None, port, None,
                slot, port.get_num_messages(slot), None, message.timestamp)

        recv_endpoints = self._peer_info.get_peer_endpoints(
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
            self._server.deposit(recv_endpoint.ref(), encoded_message)

        port.increment_num_messages(slot)

        profile_event.stop()
        if port.is_vector():
            profile_event.port_length = port.get_length()
        profile_event.message_size = len(encoded_message)
        if not isinstance(message.data, ClosePort):
            self._profiler.record_event(profile_event)

    def receive_message(
            self, port_name: str, slot: Optional[int] = None) -> Tuple[Message, float]:
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

        Returns:
            The received message, with message.settings holding
            the settings overlay. The settings attribute is
            guaranteed to not be None. Secondly, the saved_until
            metadata field from the received message.

        Raises:
            RuntimeError: If the network connection had an error, or the
                    message number was incorrect.
        """
        if port_name == 'muscle_settings_in':
            port = self._port_manager._muscle_settings_in
        else:
            port = self._port_manager.get_port(port_name)

        if slot is None:
            port_and_slot = port_name
            slot_list: List[int] = []
        else:
            port_and_slot = f"{port_name}[{slot}]"
            slot_list = [slot]
        _logger.debug('Waiting for message on {}'.format(port_and_slot))

        recv_endpoint = self.__get_endpoint(port_name, slot_list)

        receive_event = ProfileEvent(
                ProfileEventType.RECEIVE, ProfileTimestamp(), None, port, None,
                slot, port.get_num_messages())

        # peer_info already checks that there is at most one snd_endpoint
        # connected to the port we receive on
        snd_endpoint = self._peer_info.get_peer_endpoints(
                recv_endpoint.port, slot_list)[0]
        client = self.__get_client(snd_endpoint.instance())
        timeout_handler = None
        if self._receive_timeout >= 0:
            timeout_handler = ReceiveTimeoutHandler(
                    self._manager, snd_endpoint.instance(),
                    port_name, slot, self._receive_timeout)
        try:
            mpp_message_bytes, profile = client.receive(
                    recv_endpoint.ref(), timeout_handler)
        except (ConnectionError, SocketClosed) as exc:
            raise RuntimeError(
                "Error while receiving a message: connection with peer"
                f" '{snd_endpoint.kernel}' was lost. Did the peer crash?"
            ) from exc
        except Deadlock:
            # Profiler messages may be used for debugging the deadlock
            self._profiler.shutdown()
            raise RuntimeError(
                "Deadlock detected while receiving a message on "
                f"port '{port_and_slot}'. See manager logs for more detail."
            ) from None

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
                return self.receive_message(port_name, slot)
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

    def shutdown(self) -> None:
        """Shuts down the Communicator, closing connections.
        """
        self._close_ports()

        for client in self._clients.values():
            client.close()

        wait_event = ProfileEvent(ProfileEventType.DISCONNECT_WAIT, ProfileTimestamp())
        self._server.wait_for_receivers()
        self._profiler.record_event(wait_event)

        shutdown_event = ProfileEvent(ProfileEventType.SHUTDOWN, ProfileTimestamp())
        self._server.shutdown()
        self._profiler.record_event(shutdown_event)

    def __instance_id(self) -> Reference:
        """Returns our complete instance id.
        """
        return self._kernel + self._index

    def __get_client(self, instance: Reference) -> MPPClient:
        """Get or create a client to connect to the given instance.

        Args:
            instance: A reference to the instance to connect to.

        Returns:
            An existing or new MCP client.
        """
        if instance not in self._clients:
            locations = self._peer_info.get_peer_locations(instance)
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

    def _close_port(self, port_name: str, slot: Optional[int] = None) -> None:
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

    def _close_outgoing_ports(self) -> None:
        """Closes outgoing ports.

        This sends a close port message on all slots of all outgoing
        ports.
        """
        for operator, ports in self._port_manager.list_ports().items():
            if operator.allows_sending():
                for port_name in ports:
                    port = self._port_manager.get_port(port_name)
                    if port.is_vector():
                        for slot in range(port.get_length()):
                            self._close_port(port_name, slot)
                    else:
                        self._close_port(port_name)

    def _drain_incoming_port(self, port_name: str) -> None:
        """Receives messages until a ClosePort is received.

        Receives at least once.

        Args:
            port_name: Port to drain.
        """
        port = self._port_manager.get_port(port_name)
        while port.is_open():
            # TODO: log warning if not a ClosePort
            self.receive_message(port_name)

    def _drain_incoming_vector_port(self, port_name: str) -> None:
        """Receives messages until a ClosePort is received.

        Works with (resizable) vector ports.

        Args:
            port_name: Port to drain.
        """
        port = self._port_manager.get_port(port_name)
        while not all([not port.is_open(slot)
                       for slot in range(port.get_length())]):
            for slot in range(port.get_length()):
                if port.is_open(slot):
                    self.receive_message(port_name, slot)

    def _close_incoming_ports(self) -> None:
        """Closes incoming ports.

        This receives on all incoming ports until a ClosePort is
        received on them, signaling that there will be no more
        messages, and allowing the sending instance to shut down
        cleanly.
        """
        for operator, port_names in self._port_manager.list_ports().items():
            if operator.allows_receiving():
                for port_name in port_names:
                    port = self._port_manager.get_port(port_name)
                    if not port.is_connected():
                        continue
                    if not port.is_vector():
                        self._drain_incoming_port(port_name)
                    else:
                        self._drain_incoming_vector_port(port_name)

    def _close_ports(self) -> None:
        """Closes all ports.

        This sends a close port message on all slots of all outgoing
        ports, then receives one on all incoming ports.
        """
        self._close_outgoing_ports()
        self._close_incoming_ports()
