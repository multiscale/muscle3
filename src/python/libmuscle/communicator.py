import logging
from collections.abc import Iterator
from copy import deepcopy
from typing import Any, Optional, cast

from ymmsl.v0_2 import ConduitFilter, Operator, Reference, Settings

from libmuscle.communicator_state import CommunicatorState
from libmuscle.endpoint import Endpoint
from libmuscle.mcp.tcp_util import SocketClosed
from libmuscle.mmp_client import MMPClient
from libmuscle.mpp_client import MPPClient
from libmuscle.mpp_message import Milestone, MPPMessage
from libmuscle.mpp_server import MPPServer
from libmuscle.peer_info import PeerInfo
from libmuscle.port import Port
from libmuscle.port_manager import PortManager
from libmuscle.profiler import Profiler
from libmuscle.profiling import ProfileEvent, ProfileEventType, ProfileTimestamp
from libmuscle.receive_timeout_handler import Deadlock, ReceiveTimeoutHandler
from libmuscle.timeline_manager import (
    IterationCount,
    PortAndSlot,
    TimelineManager,
    get_most_nested_iteration,
)
from libmuscle.util import port_desc

_logger = logging.getLogger(__name__)


MessageObject = Any
FInitCacheType = dict[PortAndSlot, "Message"]
MPPCacheType = dict[PortAndSlot, MPPMessage]


class PortClosed(Exception):
    """Exception raised when a port was closed during the F_INIT prereceive"""


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
    def __init__(
        self,
        timestamp: float,
        next_timestamp: Optional[float] = None,
        data: MessageObject = None,
        settings: Optional[Settings] = None,
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


def _make_message(mpp_msg: MPPMessage, copy: bool = False) -> Message:
    """Create a Message object from the provided MPPMessage.
    Args:
        mpp_msg: The MPPMessage object to create the Message from.
        copy: Whether to deepcopy the data and settings.
    """
    return Message(
        mpp_msg.timestamp,
        mpp_msg.next_timestamp,
        deepcopy(mpp_msg.data) if copy else mpp_msg.data,
        deepcopy(mpp_msg.settings_overlay) if copy else mpp_msg.settings_overlay,
    )


def _yield_slots(port: Port) -> Iterator[Optional[int]]:
    """Iterator over the slots in the port."""
    if not port.is_vector():
        yield None
    else:
        yield 0  # Allow pre-receive to receive 1 message that updates port._length
        yield from range(1, port.get_length())


class Communicator:
    """Communication engine for MUSCLE3.

    This class is the mailroom for a kernel that uses MUSCLE3. It
    manages the sending and receiving of messages, although it
    leaves the actual data transmission to various protocol-specific
    servers and clients.
    """

    def __init__(
        self,
        kernel: Reference,
        index: list[int],
        port_manager: PortManager,
        profiler: Profiler,
        manager: MMPClient,
    ) -> None:
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
        self._clients: dict[Reference, MPPClient] = {}

        self._pre_receive_ports: list[Port] = []
        """List of ports that we should pre-receive on."""
        self._repeat_filters: dict[str, list[ConduitFilter]] = {}
        """List of repeat filters for each port_name with repeat filters applied."""
        self._message_cache: MPPCacheType = {}
        """Message cache for pre-received messages."""

        self._reduced_count: dict[Reference, int] = {}
        """Size of IterationCount, after applying the reducer filters, per peer port.

        Keys are references to peer ports: ``component + port``. The reduced count is
        the size of the IterationCount after applying the reducer filters and determines
        in which (parent) timeline these messages are sent.

        If our timeline is ":macro:micro" then:
        - reduced_count = 0: send on the root (":") timeline
        - reduced_count = 1: send on the ":macro" timeline
        - reduced_count = 2: send on the ":macro:micro" timeline
        """
        self._reducer_cache: dict[Reference, MPPMessage] = {}
        """Message cache for reducer filters."""

    def get_locations(self) -> list[str]:
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
        messages accordingly. The TimelineManager is also created here, since it
        needs the port manager's ports to already be connected to their peers.

        Args:
            peer_info: Information about the peers.
        """
        self._timeline = self._manager.get_timeline()
        self._peer_info = peer_info
        self._timeline_manager = TimelineManager(self._port_manager, self._timeline)
        self._prepare_conduit_filters()

    def set_receive_timeout(self, receive_timeout: float) -> None:
        """Update the timeout after which the manager is notified that we are waiting
        for a message.

        Args:
            receive_timeout: Timeout (seconds). A negative number disables the deadlock
                notification mechanism.
        """
        self._receive_timeout = receive_timeout

    def get_state(self) -> CommunicatorState:
        """Return the current internal state for checkpointing.

        This includes states for the communicator, port manager and timeline manager.
        """
        return CommunicatorState(
            self._port_manager.get_message_counts(),
            self._timeline_manager.get_state(),
            self._message_cache,
        )

    def restore_state(self, state: CommunicatorState) -> None:
        """Restore a previously saved state.

        Args:
            state: The state to restore, as returned by get_state().
        """
        self._port_manager.restore_message_counts(state.port_message_counts)
        self._timeline_manager.restore_state(state.timeline_state)
        self._message_cache = state.message_cache

    def send_message(
        self,
        port_name: str,
        message: Message,
        slot: Optional[int] = None,
    ) -> None:
        """Send a message and settings to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        port = self._port_manager.get_port(port_name)
        if not port.is_connected():
            _logger.debug(
                "Sending message on unconnected port %s", port_desc(port_name, slot)
            )
            return
        if not port.is_open(slot):
            if (
                isinstance(message.data, Milestone)
                and message.data.is_final_milestone()
            ):
                return  # Ignore closing an already closed port
            raise RuntimeError(f"Port {port_desc(port_name, slot)} is already closed.")
        _logger.debug("Sending message on %s", port_desc(port_name, slot))

        if isinstance(message.data, Milestone):
            iteration = message.data.iteration
        else:
            iteration = self._timeline_manager.check_send_message(port_name, slot)

        profile_event = ProfileEvent(
            ProfileEventType.SEND,
            ProfileTimestamp(),
            None,
            port,
            None,
            slot,
            port.get_num_messages(slot),
            None,
            message.timestamp,
        )

        port_length = None
        if port.is_resizable():
            port_length = port.get_length()

        snd_endpoint, recv_endpoints = self._get_endpoints(port, slot)
        for recv_endpoint in recv_endpoints:
            mpp_message = MPPMessage(
                snd_endpoint.ref(),
                recv_endpoint.ref(),
                port_length,
                message.timestamp,
                message.next_timestamp,
                cast(Settings, message.settings),
                port.get_num_messages(slot),
                message.data,
                iteration,
            )
            peer_port = recv_endpoint.kernel + recv_endpoint.port
            if peer_port in self._reduced_count:
                result = self._apply_reduce_filters(peer_port, mpp_message)
                if result is None:
                    continue
                mpp_message = result
            encoded_message = mpp_message.encoded()
            profile_event.message_size = len(memoryview(encoded_message))
            self._server.deposit(recv_endpoint.ref(), encoded_message)

        profile_event.stop()
        if port.is_vector():
            profile_event.port_length = port.get_length()
        if not isinstance(message.data, Milestone):
            self._profiler.record_event(profile_event)
            port.increment_num_messages(slot)
        elif message.data.is_final_milestone():
            port.set_closed(slot)

    def _apply_reduce_filters(
        self, peer_port: Reference, message: MPPMessage
    ) -> Optional[MPPMessage]:
        """Apply reduce filters to a message sent on a conduit with reduce filters.

        User-provided messages (through instance.send()) will be stored (overwriting any
        existing message). For milestones this method decides if the milestone should be
        sent, or a cached message, or nothing at all.

        Args:
            peer_port: Peer port (component + port) to send to.
            message: MPPMessage to be checked.

        Returns:
            The MPPMessage to send, or None if we do not need to send anything.
        """
        message.message_number = -1  # GH#411: Disabled checkpointing for reducer filter

        reduced_count = self._reduced_count[peer_port]

        if not isinstance(message.data, Milestone):
            # Reduce the message iteration count to match with the timeline we send to
            message.iteration = message.iteration[:reduced_count]
            self._reducer_cache[message.receiver] = message
            _logger.debug("Message for %s stored in cache", message.receiver)
            return None

        # Decide whether to send the milestone, ignore it, or send a cached message.
        n_milestone = len(message.data.iteration)
        if n_milestone < reduced_count:
            # Milestone from ancestor timeline: send it
            return message

        elif n_milestone == reduced_count:
            # This is the target timeline after reduce filters applied: we need to
            # send the cached message (or make up an empty one) and discard the
            # milestone:
            cached_msg = self._reducer_cache.pop(message.receiver, None)
            if cached_msg is None:
                _logger.info(
                    "No cached message available to send because this instance did "
                    "not run. Sending an empty message to %s instead.",
                    message.receiver,
                )
                message.data = None
                return message

            assert cached_msg.iteration == message.iteration
            _logger.debug("Sending cached message to %s", message.receiver)
            return cached_msg

        else:
            _logger.debug(
                "Ignored %s for %s because of LAST filters.",
                message.data,
                message.receiver,
            )
            return None

    def pre_receive(self) -> FInitCacheType:
        """Pre-receive on all connected F_INIT ports and S ports with repeat filters.

        Returns:
            The received messages on F_INIT ports (including muscle_settings_in).
        """
        finished_iteration = self._timeline_manager.start_reuse_iteration()
        milestone_iteration = finished_iteration

        while True:
            if milestone_iteration is not None:
                # Should send on O_I only when this is the milestone for the finished
                # iteration. Other milestones (received on F_INIT ports) should
                # propagate to O_F as well:
                milestone = Milestone(milestone_iteration)
                self._broadcast_milestone(
                    milestone, only_o_i=(milestone_iteration == finished_iteration)
                )

                # Clean up stale messages in the cache
                self._message_cache = {
                    key: message
                    for key, message in self._message_cache.items()
                    if message.iteration != milestone_iteration
                }

                if milestone.is_final_milestone():
                    raise PortClosed()

            milestone_iterations: list[IterationCount] = []
            # Pre-receive on all F_INIT ports and repeated S ports, if needed
            for port in self._pre_receive_ports:
                port_name = str(port.name)
                for slot in _yield_slots(port):
                    if (port_name, slot) in self._message_cache:
                        continue
                    _logger.debug("Pre-receiving on %s", port_desc(port_name, slot))
                    mpp_message = self._receive_message(port_name, slot)
                    self._message_cache[(port_name, slot)] = mpp_message

                    if isinstance(mpp_message.data, Milestone):
                        milestone_iterations.append(mpp_message.data.iteration)

            if not milestone_iterations:
                break  # No milestones received, we have only messages now

            # Handle most deeply nested milestone first:
            try:
                milestone_iteration = get_most_nested_iteration(milestone_iterations)
            except ValueError as exc:
                raise RuntimeError(
                    "Internal error: received milestones for incompatible iterations "
                    f"during F_INIT: {milestone_iterations}"
                ) from exc

        # Update current iteration
        new_iteration = self._timeline_manager.check_pre_received_iteration_counts(
            [msg.iteration for msg in self._message_cache.values()]
        )

        # Sanity check: we should not have any milestones in the cache at this point
        if any(isinstance(msg.data, Milestone) for msg in self._message_cache.values()):
            raise RuntimeError("Internal error: found milestones in message cache.")

        # Fill F_INIT cache for Instance
        cache: FInitCacheType = {}
        for port in self._port_manager.get_connected_ports(Operator.F_INIT):
            port_name = str(port.name)
            filters = self._repeat_filters.get(port_name, [])
            pad_message = self._pad_message(new_iteration, filters)
            for slot in _yield_slots(port):
                mpp_message = self._message_cache[(port_name, slot)]
                message = _make_message(mpp_message)
                if pad_message:
                    message.data = None
                cache[(port_name, slot)] = message

        return cache

    def receive_s_message(self, port_name: str, slot: Optional[int] = None) -> Message:
        """Receive a message and attached settings overlay on an "S" port.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        Args:
            port_name: The port on which a message is to be received.
            slot: The slot to receive the message on, if any.

        Returns:
            The received message, with message.settings holding
            the settings overlay. The settings attribute is
            guaranteed to not be None.

        Raises:
            RuntimeError: If the network connection had an error, or the
                    message number was incorrect.
        """
        self._timeline_manager.check_receive_s(port_name, slot)

        # Handle receive on repeated S port:
        if port_name in self._repeat_filters:
            filters = self._repeat_filters[port_name]
            message = self._message_cache[(port_name, slot)]
            cur_iteration = self._timeline_manager.record_received_s_message(
                port_name, slot, message.iteration, len(filters)
            )
            result = _make_message(message, copy=True)
            if self._pad_message(cur_iteration, filters):
                result.data = None
            return result

        # Instance should not need to bother about milestones, so we keep receiving
        # messages until we have actual data:
        while True:
            message = self._receive_message(port_name, slot)
            if isinstance(message.data, Milestone):
                if message.data.is_final_milestone():
                    raise PortClosed()
            else:
                self._timeline_manager.record_received_s_message(
                    port_name, slot, message.iteration
                )
                return _make_message(message)

    def _receive_message(self, port_name: str, slot: Optional[int]) -> MPPMessage:
        """Implementation for receive_message."""
        port = self._port_manager.get_port(port_name)
        port_and_slot = port_desc(port_name, slot)
        _logger.debug("Waiting for message on %s", port_and_slot)

        receive_event = ProfileEvent(
            ProfileEventType.RECEIVE,
            ProfileTimestamp(),
            None,
            port,
            None,
            slot,
            port.get_num_messages(),
        )

        # peer_info already checks that there is at most one snd_endpoint
        # connected to the port we receive on
        recv_endpoint, (snd_endpoint,) = self._get_endpoints(port, slot)
        client = self._get_client(snd_endpoint.instance())
        timeout_handler = None
        if self._receive_timeout >= 0:
            timeout_handler = ReceiveTimeoutHandler(
                self._manager,
                snd_endpoint.instance(),
                port_name,
                slot,
                self._receive_timeout,
            )
        try:
            mpp_message_bytes, profile = client.receive(
                recv_endpoint.ref(), timeout_handler
            )
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
            ProfileEventType.RECEIVE_DECODE,
            ProfileTimestamp(),
            None,
            port,
            None,
            slot,
            port.get_num_messages(),
            len(memoryview(mpp_message_bytes)),
        )
        mpp_message = MPPMessage.from_bytes(mpp_message_bytes)
        recv_decode_event.stop()

        if mpp_message.port_length is not None:
            if port.is_resizable():
                port.set_length(mpp_message.port_length)

        milestone: Optional[Milestone] = None
        if isinstance(mpp_message.data, Milestone):
            milestone = mpp_message.data
            if milestone.is_final_milestone():
                port.set_closed(slot)

        recv_wait_event = ProfileEvent(
            ProfileEventType.RECEIVE_WAIT,
            profile[0],
            profile[1],
            port,
            mpp_message.port_length,
            slot,
            port.get_num_messages(),
            len(memoryview(mpp_message_bytes)),
            mpp_message.timestamp,
        )

        recv_xfer_event = ProfileEvent(
            ProfileEventType.RECEIVE_TRANSFER,
            profile[1],
            profile[2],
            port,
            mpp_message.port_length,
            slot,
            port.get_num_messages(),
            len(memoryview(mpp_message_bytes)),
            mpp_message.timestamp,
        )

        recv_decode_event.message_timestamp = mpp_message.timestamp
        receive_event.message_timestamp = mpp_message.timestamp

        if port.is_vector():
            receive_event.port_length = port.get_length()
            recv_wait_event.port_length = port.get_length()
            recv_xfer_event.port_length = port.get_length()
            recv_decode_event.port_length = port.get_length()

        receive_event.message_size = len(memoryview(mpp_message_bytes))

        if milestone is None or not milestone.is_final_milestone():
            # Don't log receives of final milestone: this is recorded as SHUTDOWN_WAIT
            self._profiler.record_event(recv_wait_event)
            self._profiler.record_event(recv_xfer_event)
            self._profiler.record_event(recv_decode_event)
            self._profiler.record_event(receive_event)

        expected_message_number = port.get_num_messages(slot)
        if (
            mpp_message.message_number >= 0  # GH#411: negative for reducer filters
            and expected_message_number != mpp_message.message_number
        ):
            if (
                expected_message_number - 1 == mpp_message.message_number
                and port.is_resuming(slot)
            ):
                _logger.debug(
                    f"Discarding received message on {port_and_slot}"
                    ": resuming from weakly consistent snapshot"
                )
                if milestone is None:
                    port.set_resumed(slot)
                return self._receive_message(port_name, slot)
            raise RuntimeError(
                f"Received message on {port_and_slot} with"
                " unexpected message number"
                f" {mpp_message.message_number}. Was expecting"
                f" {expected_message_number}. Are you resuming"
                " from an inconsistent snapshot?"
            )

        if milestone is None:
            port.increment_num_messages(slot)
            _logger.debug(f"Received message on {port_and_slot}")
        elif milestone.is_final_milestone():
            _logger.debug(f"Port {port_and_slot} is now closed")
        else:
            _logger.debug("Received %s on %s", milestone, port_and_slot)

        return mpp_message

    def shutdown(self) -> None:
        """Shuts down the Communicator, closing connections."""
        self._close_ports()

        for client in self._clients.values():
            client.close()

        wait_event = ProfileEvent(ProfileEventType.DISCONNECT_WAIT, ProfileTimestamp())
        self._server.wait_for_receivers()
        self._profiler.record_event(wait_event)

        shutdown_event = ProfileEvent(ProfileEventType.SHUTDOWN, ProfileTimestamp())
        self._server.shutdown()
        self._profiler.record_event(shutdown_event)

    def _get_client(self, instance: Reference) -> MPPClient:
        """Get or create a client to connect to the given instance.

        Args:
            instance: A reference to the instance to connect to.

        Returns:
            An existing or new MCP client.
        """
        if instance not in self._clients:
            locations = self._peer_info.get_peer_locations(instance)
            _logger.info(f"Connecting to peer {instance} at {locations}")
            self._clients[instance] = MPPClient(locations)

        return self._clients[instance]

    def _get_endpoints(
        self, port: Port, slot: Optional[int]
    ) -> tuple[Endpoint, list[Endpoint]]:
        """Return our endpoint and the peer endpoints for the given port and slot."""
        return (
            Endpoint(self._kernel, self._index, port.name, slot),
            self._peer_info.get_peer_endpoints(port.name, slot),
        )

    def _broadcast_milestone(self, milestone: Milestone, only_o_i: bool) -> None:
        """Send a Milestone to all O_I (and optionally O_F) ports/slots.

        Args:
            milestone: The Milestone to send.
            only_o_i: Set to True to only send to connected O_I ports.
        """
        _logger.debug(
            "Sending %s to all %s ports.", milestone, "O_I" if only_o_i else "outgoing"
        )
        message = Message(float("-inf"), data=milestone, settings=Settings())

        def do_broadcast(op: Operator) -> None:
            for port in self._port_manager.get_connected_ports(op):
                port_name = str(port.name)
                if port.is_vector():
                    for slot in range(port.get_length()):
                        self.send_message(port_name, message, slot)
                else:
                    self.send_message(port_name, message)

        do_broadcast(Operator.O_I)
        if not only_o_i:
            do_broadcast(Operator.O_F)

    def _close_outgoing_ports(self) -> None:
        """Closes outgoing ports.

        This broadcasts the root Milestone message on all slots of all outgoing ports.
        """
        self._broadcast_milestone(Milestone([]), False)

    def _drain_incoming_port(self, port_name: str) -> None:
        """Receives messages until the scalar port is closed."""
        port = self._port_manager.get_port(port_name)
        while port.is_open():
            # TODO: log warning if not a Milestone
            self._receive_message(port_name, None)

    def _drain_incoming_vector_port(self, port_name: str) -> None:
        """Receives messages until the vector port is closed."""
        port = self._port_manager.get_port(port_name)
        while not all([not port.is_open(slot) for slot in range(port.get_length())]):
            for slot in range(port.get_length()):
                if port.is_open(slot):
                    self._receive_message(port_name, slot)

    def _close_incoming_ports(self) -> None:
        """Closes incoming ports.

        This receives on all incoming ports until the port is closed. This signals that
        there will be no more messages, and allows the sending instance to shut down
        cleanly.
        """
        for operator in (Operator.F_INIT, Operator.S):
            for port in self._port_manager.get_connected_ports(operator):
                port_name = str(port.name)
                try:
                    if not port.is_vector():
                        self._drain_incoming_port(port_name)
                    else:
                        self._drain_incoming_vector_port(port_name)
                except RuntimeError:
                    peer_port = self._peer_info.get_peer_ports(port.name)[0]
                    peer_name = str(peer_port[:-1])
                    _logger.warning(
                        "Connection with peer '%s' was lost at the end of the "
                        "simulation, probably because it crashed.",
                        peer_name,
                    )

    def _close_ports(self) -> None:
        """Closes all ports.

        This sends a close port message on all slots of all outgoing
        ports, then receives one on all incoming ports.
        """
        if not hasattr(self, "_peer_info"):
            return  # Not connected yet, no ports to close
        self._close_outgoing_ports()
        self._close_incoming_ports()

    def _prepare_conduit_filters(self) -> None:
        """Check which ports are connected with a conduit filter and initialize the
        associated logic.
        """
        peer_info = self._peer_info
        # Repeater filters
        for operator in (Operator.F_INIT, Operator.S):
            for port in self._port_manager.get_connected_ports(operator):
                filters = peer_info.get_filters_for_receiver(self._kernel + port.name)
                # Only keep the repeater filters, the sending component handles reducers
                filters = [filter for filter in filters if filter.is_repeater()]
                if filters:
                    self._repeat_filters[str(port.name)] = filters
                if operator is Operator.F_INIT or filters:
                    self._pre_receive_ports.append(port)

        # Reducer filters
        for operator in (Operator.O_I, Operator.O_F):
            for port in self._port_manager.get_connected_ports(operator):
                for peer_port in peer_info.get_peer_ports(port.name):
                    filters = peer_info.get_filters_for_receiver(peer_port)
                    # Count the reducer filters, receiving component handles repeaters
                    n_reducers = sum(1 for filter in filters if filter.is_reducer())
                    if n_reducers > 0:
                        self._reduced_count[peer_port] = (
                            len(self._timeline) + len(port.timeline) - n_reducers
                        )

    def _pad_message(
        self, cur_iteration: IterationCount, filters: list[ConduitFilter]
    ) -> bool:
        """Check if we should pad the message in the current iteration, based on the
        configured pad/repeat filters.

        Returns:
            True if the message data should be nilled, False otherwise.
        """
        return any(
            filter is ConduitFilter.PAD and cur_iteration[-len(filters) + i] > 0
            for i, filter in enumerate(filters)
        )
