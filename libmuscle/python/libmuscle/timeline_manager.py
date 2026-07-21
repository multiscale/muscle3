import logging
from dataclasses import dataclass
from typing import Optional, TypedDict

from typing_extensions import TypeAlias
from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager

_logger = logging.getLogger(__name__)


PortAndSlot: TypeAlias = tuple[str, Optional[int]]  # (port_name, slot)


class SubTimelineState(TypedDict):
    """A single sub-timeline's state, as returned by
    SubTimelineManager.get_state() for saving in a snapshot."""

    iteration: Optional[list[int]]
    first_operator: Optional[str]
    send_participated: list[PortAndSlot]
    receive_participated: list[PortAndSlot]
    ever_used: bool


@dataclass
class TimelineState:
    """The main timeline's iteration and participation, and every
    sub-timeline's state.

    Returned by TimelineManager.get_state() for saving in a snapshot, and
    passed back into TimelineManager.restore_state() to resume from one.
    """

    iteration: list[int]
    send_participated: list[PortAndSlot]
    receive_participated: list[PortAndSlot]
    subtimeline_states: dict[str, SubTimelineState]


def _slots(port: Port) -> list[Optional[int]]:
    """Return the slot indices of a port, or [None] if it's scalar."""
    if port.is_vector():
        return list(range(port.get_length()))
    return [None]


def _count_slots(ports: list[Port]) -> int:
    """Return the total number of port/slot combinations, where a vector port counts
    once per slot.
    """
    return sum(len(_slots(port)) for port in ports)


def _all_participated(participated: set[PortAndSlot], count: int) -> bool:
    """Return True if every one of count port/slot combinations has participated.

    Args:
        participated: The (name, slot) combinations that have already sent or
            received a message for the current (sub-)iteration.
        count: The total number of port/slot combinations expected to participate.

    Returns:
        True if every expected port/slot combination has participated.
    """
    return len(participated) == count


def _reset_participation(*participated: set[PortAndSlot]) -> None:
    """Clear each given set, marking every port and slot as not participated.

    Args:
        participated: One or more sets of (name, slot) combinations to clear.
    """
    for p in participated:
        p.clear()


def _subtimeline_complete(stm: "SubTimelineManager") -> bool:
    """Return whether a subtimeline is done with this cycle.

    If it was used this cycle, every one of its ports must have
    participated. If it wasn't used this cycle, that's only fine if it has
    been used in some earlier cycle (e.g. a cache skipping a refresh); a
    sub-timeline that has never been used at all is not considered complete,
    since it would then never be used for the lifetime of the instance.
    """
    if stm._iteration is not None:
        return _all_participated(
            stm._send_participated, stm._num_send_slots
        ) and _all_participated(stm._receive_participated, stm._num_receive_slots)
    return stm._ever_used


class TimelineManager:
    """Tracks iteration state for the main timeline and manages it's sub-timelines.

    O_F and F_INIT ports live on the main timeline, tracked directly by this manager.
    O_I and S ports live on sub-timelines, each tracked by its own SubTimelineManager,
    grouped by the port's timeline attribute.

    Every TimelineManager and SubTimelineManager records, for each of its
    ports, whether that port has already sent or received a message for the
    current iteration, as a set of (port name, slot) tuples, split by
    direction: one set for the ports that send (O_F or O_I) and one for the
    ports that receive (F_INIT or S).
    """

    def __init__(self, port_manager: PortManager) -> None:
        """Create a TimelineManager.

        The sub-timelines cannot be determined yet, since port.timeline is only
        populated once the ports have been connected to their peers.

        Args:
            port_manager: The port manager for this instance.
        """
        self._port_manager = port_manager
        self._iteration: Optional[list[int]] = None
        self._send_ports: list[Port] = []
        self._receive_ports: list[Port] = []
        self._num_send_slots = 0
        self._num_receive_slots = 0
        self._send_participated: set[PortAndSlot] = set()
        self._receive_participated: set[PortAndSlot] = set()
        self._subtimelines: dict[Timeline, SubTimelineManager] = {}

    def on_ports_connected(self) -> None:
        """Create the SubTimelineManagers once the ports are connected. It also collects
        the main-timeline (F_INIT and O_F) ports and their participation tracking, and
        starts the main timeline at [] right away if it has no F_INIT message to wait
        for.
        """
        all_ports = self._port_manager.list_ports()

        self._receive_ports = [
            self._port_manager.get_port(name)
            for name in all_ports.get(Operator.F_INIT, [])
            if self._port_manager.get_port(name).is_connected()
        ]
        # muscle_settings_in is F_INIT too, but it's not a declared port, so
        # list_ports() doesn't return it; check_receive/check_received_message
        # do treat it as F_INIT though, so it must be tracked here as well.
        if self._port_manager.settings_in_connected():
            self._receive_ports.append(
                self._port_manager.get_port("muscle_settings_in")
            )
        self._send_ports = [
            self._port_manager.get_port(name)
            for name in all_ports.get(Operator.O_F, [])
            if self._port_manager.get_port(name).is_connected()
        ]
        self._num_receive_slots = _count_slots(self._receive_ports)
        self._num_send_slots = _count_slots(self._send_ports)

        subtimelines = self._port_manager.list_subtimelines()

        # Assumes every O_I/S port has a non-empty timeline.
        self._subtimelines = {
            tl: SubTimelineManager(tl, self._port_manager) for tl in subtimelines
        }

        # A component with no connected F_INIT ports has no F_INIT message to
        # learn its iteration from, so its main timeline starts at [].
        self._iteration = None if self._has_connected_f_init() else []

    def get_state(self) -> TimelineState:
        """Return the main timeline's iteration and participation, and every
        sub-timeline's state, for saving in a snapshot.

        Raises:
            RuntimeError: If the main timeline has not started yet, because
                this component has connected F_INIT ports and none have been
                received yet. Make sure this is only called once F_INIT has
                been received.
        """
        if self._iteration is None:
            raise RuntimeError(
                "Cannot save a snapshot: this instance has connected F_INIT"
                " ports, but hasn't received a message on any of them yet."
                " Make sure a snapshot is only saved after this instance has"
                " started receiving messages."
            )
        return TimelineState(
            iteration=self._iteration,
            send_participated=list(self._send_participated),
            receive_participated=list(self._receive_participated),
            subtimeline_states={
                str(tl): stm.get_state() for tl, stm in self._subtimelines.items()
            },
        )

    def cycle_complete(self) -> bool:
        """Return whether every main-timeline port has participated and
        every sub-timeline has either completed a sub-iteration or wasn't
        used at all this cycle.
        """
        return (
            _all_participated(self._receive_participated, self._num_receive_slots)
            and _all_participated(self._send_participated, self._num_send_slots)
            and all(_subtimeline_complete(stm) for stm in self._subtimelines.values())
        )

    def _has_connected_f_init(self) -> bool:
        """Return whether this component has any connected F_INIT ports,
        including muscle_settings_in."""
        return bool(self._receive_ports)

    def check_send_message(
        self, port_name: str, slot: Optional[int] = None
    ) -> list[int]:
        """Check and update the timeline state before sending on the given port.

        By the time a send is possible, Instance has already received a message on
        every F_INIT port for the current iteration, so this delegates straight to
        the specific checks for the O_F or O_I port and returns the iteration of
        its timeline.

        Args:
            port_name: Name of the O_F or O_I port that is about to send.
            slot: The slot being sent on, if this is a vector port.

        Returns:
            The iteration to embed in the outgoing message.
        """
        port = self._port_manager.get_port(port_name)
        assert self._iteration is not None, (
            "Instance always receives on every F_INIT port before O_F/O_I can send"
        )

        if port.operator is Operator.O_F:
            return self._check_send_o_f(port_name, slot)

        return self._subtimelines[port.timeline].check_send_message(
            port, slot, self._iteration
        )

    def _check_send_o_f(self, port_name: str, slot: Optional[int]) -> list[int]:
        """Check the O_F-specific send conditions, update state, and return
        the iteration to embed in the outgoing message.

        An O_F port requires that it has not already sent for the current iteration and
        that every sub-timeline has either completed a sub-iteration or wasn't used at
        all this iteration.

        Args:
            port_name: Name of the O_F port that is about to send.
            slot: The slot being sent on, if this is a vector port.

        Returns:
            The iteration to embed in the outgoing message.

        Raises:
            RuntimeError: If this port already sent a message for the current
                iteration, or a sub-timeline was used but hasn't completed a
                sub-iteration.
        """
        assert self._iteration is not None
        key = (port_name, slot)
        if key in self._send_participated:
            raise RuntimeError(
                f'Port "{port_name}" already sent a message for this iteration.'
            )

        for stm in self._subtimelines.values():
            if not _subtimeline_complete(stm):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but a'
                    " sub-timeline has not completed a sub-iteration yet."
                )

        self._send_participated.add(key)
        return self._iteration

    def restore_state(self, state: TimelineState) -> None:
        """Restore the main timeline and every sub-timeline, for snapshot resume.

        Resets everything first, then restores the main timeline's iteration, per-port
        participation, and every sub-timeline's state from the snapshot.

        Args:
            state: The saved timeline state, as returned by get_state().
        """
        self.reset()
        self._iteration = state.iteration
        self._send_participated = {
            (port_name, slot) for port_name, slot in state.send_participated
        }
        self._receive_participated = {
            (port_name, slot) for port_name, slot in state.receive_participated
        }
        for tl, stm in self._subtimelines.items():
            sub_state = state.subtimeline_states.get(str(tl))
            if sub_state is not None:
                stm.restore_state(sub_state)

    def check_receive(self, port_name: str, slot: Optional[int] = None) -> None:
        """Check that receiving on the given port is currently allowed.

        An F_INIT port may always receive before the main timeline has
        started, and afterwards may receive again as long as it has not
        already received a message for the current iteration.

        S may receive straight away if the component has no connected F_INIT ports,
        otherwise it must first receive a message on every F_INIT port. Once that
        is satisfied, whether this specific S port may receive is delegated to
        the corresponding SubTimelineManager.

        Args:
            port_name: Name of the F_INIT or S port about to receive.
            slot: The slot being received on, if this is a vector port.

        Raises:
            RuntimeError: If this F_INIT port already received a message for
                the current iteration, if this S port's component has
                connected F_INIT ports and has not yet received on every one
                of them.
        """
        port = self._port_manager.get_port(port_name)

        if port.operator is Operator.F_INIT:
            if (port_name, slot) in self._receive_participated:
                raise RuntimeError(
                    f'Port "{port_name}" already received a message for this iteration.'
                )
            return

        if port.operator is Operator.S:
            if self._iteration is None:
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive the first message,'
                    " but this component has connected F_INIT ports and must"
                    " receive on all of them first."
                )
            if not _all_participated(
                self._receive_participated, self._num_receive_slots
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            self._subtimelines[port.timeline].check_receive(port, slot)
            return

    def check_received_message(
        self,
        port_name: str,
        iteration: Optional[list[int]],
        slot: Optional[int] = None,
    ) -> None:
        """Record that a message has been received on the given port.

        check_receive already established that this receive is allowed.

        For an F_INIT port, if the main timeline has not started yet, its
        iteration is adopted from the message, otherwise the message must carry
        the same iteration the main timeline is already on.

        For an S port, recording the message is delegated directly to the
        corresponding SubTimelineManager.

        Args:
            port_name: Name of the F_INIT or S port a message was received
                on.
            iteration: The iteration the received message was sent with.
            slot: The slot the message was received on, if this is a vector
                port.

        Raises:
            RuntimeError: If the message did not carry an iteration, or if an
                F_INIT port received a message with an iteration different
                from the one the main timeline is on.
        """
        port = self._port_manager.get_port(port_name)

        if iteration is None:
            raise RuntimeError(
                f'Port "{port_name}" received a message without an iteration.'
            )

        if port.operator is Operator.F_INIT:
            if self._iteration is None:
                self._iteration = iteration
            elif iteration != self._iteration:
                raise RuntimeError(
                    f'Port "{port_name}" received a message with iteration'
                    f" {iteration}, but the main timeline is at iteration"
                    f" {self._iteration}."
                )
            self._receive_participated.add((port_name, slot))
            return

        self._subtimelines[port.timeline].check_received_message(
            port_name, slot, iteration
        )

    def reset(self) -> None:
        """Reset the main timeline and it's sub-timelines.

        Clears the main timeline's iteration (back to [] if there are no connected
        F_INIT ports to wait for) and participation state, and resets every sub-timeline
        in turn.
        """
        self._iteration = None if self._has_connected_f_init() else []
        _reset_participation(self._send_participated, self._receive_participated)
        for stm in self._subtimelines.values():
            stm.reset()


class SubTimelineManager:
    """Tracks iteration state for a single sub-timeline."""

    def __init__(
        self, subtimeline: Optional[Timeline], port_manager: PortManager
    ) -> None:
        """Create a SubTimelineManager.

        Args:
            subtimeline: The timeline this manager tracks.
            port_manager: The port manager; used to look up the O_I and S ports
                belonging to this sub-timeline.
        """
        self._subtimeline = subtimeline
        self._iteration: Optional[list[int]] = None
        self._first_operator: Optional[Operator] = None
        self._ever_used = False
        """Whether this sub-timeline has been used in some cycle, current or
        past. Unlike _iteration, this is not cleared by reset()."""

        self._send_ports = [
            port_manager.get_port(name)
            for name in port_manager.list_ports(subtimeline).get(Operator.O_I, [])
            if port_manager.get_port(name).is_connected()
        ]
        self._receive_ports = [
            port_manager.get_port(name)
            for name in port_manager.list_ports(subtimeline).get(Operator.S, [])
            if port_manager.get_port(name).is_connected()
        ]
        self._num_send_slots = _count_slots(self._send_ports)
        self._num_receive_slots = _count_slots(self._receive_ports)
        self._send_participated: set[PortAndSlot] = set()
        self._receive_participated: set[PortAndSlot] = set()

    def check_send_message(
        self, port: Port, slot: Optional[int], parent_iteration: list[int]
    ) -> list[int]:
        """Check and update this sub-timeline's iteration state before sending.

        The first message sent on any O_I port (or slot of it) of this sub-timeline
        starts its iteration, establishes O_I as the operator that leads this
        sub-timeline: from then on, every sub-iteration follows the order O_I-S, and
        once every O_I and S port (and slot) of this sub-timeline has participated, that
        advances to the next sub-iteration.

        If S led instead, the order is reversed to S-O_I: this O_I port may
        not send its message for the current sub-iteration until every S port
        (and slot) has received one, and a second send on the same O_I port
        and slot before that happens is rejected.

        Args:
            port: The O_I port that is about to send.
            slot: The slot being sent on, if this is a vector port.
            parent_iteration: The main timeline's current iteration.

        Returns: The sub-timeline iteration.

        Raises:
            RuntimeError: If this port and slot has not yet sent a message
                for the current sub-iteration and S led this sub-timeline
                with only some, not all, of its S ports having received yet;
                or if it already sent one and either S led this sub-timeline
                (only a receive on S may advance it) or not every port of
                this sub-timeline has participated yet.
        """
        port_name = str(port.name)
        key = (port_name, slot)
        self._ever_used = True

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
            self._first_operator = Operator.O_I
        elif key not in self._send_participated:
            if self._first_operator is Operator.S and not _all_participated(
                self._receive_participated, self._num_receive_slots
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but only'
                    " some of this sub-timeline's S ports have received so far."
                )
        else:
            if self._first_operator is not Operator.O_I:
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but S received'
                    " first on this sub-timeline, so only a receive on S can"
                    " advance to the next sub-iteration, not a send on O_I."
                )
            if not (
                _all_participated(self._send_participated, self._num_send_slots)
                and _all_participated(
                    self._receive_participated, self._num_receive_slots
                )
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but it already'
                    " sent one for this sub-iteration and not every port of this"
                    " sub-timeline has participated yet."
                )
            self._iteration[-1] += 1
            _reset_participation(self._send_participated, self._receive_participated)

        self._send_participated.add(key)
        return list(self._iteration)

    def check_receive(self, port: Port, slot: Optional[int] = None) -> None:
        """Check that receiving on the given S port is currently allowed.

        If this S port has not yet received for the current sub-iteration, it may do so
        as long as O_I did not lead this sub-timeline, or every O_I port has already
        sent (whether O_I led is unset until the first send or receive, so before that
        this S port is always free to receive, establishing S as the leader).

        If this S port already received for the current sub-iteration, it may receive
        again only if S led this sub-timeline and every port of this sub-timeline has
        participated. If O_I led instead, only a send on O_I can advance the
        sub-iteration, so a second receive on S before that happens is rejected here.

        Args:
            port: The S port that is about to receive.
            slot: The slot being received on, if this is a vector port.

        Raises:
            RuntimeError: If this S port has not yet received for the
                current sub-iteration and only some, not all, of this
                sub-timeline's O_I ports have sent so far; or if it already
                received for the current sub-iteration and either O_I led
                this sub-timeline (only a send on O_I may advance it), or
                not every port of this sub-timeline has participated yet.
        """
        port_name = str(port.name)

        if (port_name, slot) not in self._receive_participated:
            if self._first_operator is Operator.O_I and not _all_participated(
                self._send_participated, self._num_send_slots
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive a message, but only'
                    " some of this sub-timeline's O_I ports have sent so far."
                )
            return

        if self._first_operator is not Operator.S:
            raise RuntimeError(
                f'Port "{port_name}" tried to receive a message, but O_I sent'
                " first on this sub-timeline, so only a send on O_I can"
                " advance to the next sub-iteration, not a receive on S."
            )
        if not (
            _all_participated(self._send_participated, self._num_send_slots)
            and _all_participated(self._receive_participated, self._num_receive_slots)
        ):
            raise RuntimeError(
                f'Port "{port_name}" tried to receive a message, but it already'
                " received one for this sub-iteration and not every port of"
                " this sub-timeline has participated yet."
            )

    def check_received_message(
        self, port_name: str, slot: Optional[int], iteration: list[int]
    ) -> None:
        """Record that a message has been received on the given S port.

        If this sub-timeline has not started yet, its iteration is adopted from the
        message and S is recorded as the operator that leads this sub-timeline. If this
        port and slot has not yet received for the current sub-iteration, the message
        must carry that same iteration.

        If this port and slot already received for the current sub-iteration (only
        possible when S leads and every port of this sub-timeline has participated),
        this sub-timeline never advances its iteration by adopting the message's
        iteration directly, but only once it is for a strictly later iteration than the
        current one.

        Args:
            port_name: Name of the S port a message was received on.
            slot: The slot the message was received on, if this is a vector port.
            iteration: The iteration the received message was sent with.

        Raises:
            RuntimeError: If this port and slot has not yet received for the
                current sub-iteration and the message's iteration does not
                match this sub-timeline's current iteration; or if it already
                received for the current sub-iteration and the message's
                iteration is not strictly later than the current one.
        """
        key = (port_name, slot)
        self._ever_used = True

        if self._iteration is None:
            self._iteration = iteration
            self._first_operator = Operator.S
        elif key not in self._receive_participated:
            if iteration != self._iteration:
                raise RuntimeError(
                    f'Port "{port_name}" received a message with iteration'
                    f" {iteration}, but this sub-timeline is at iteration"
                    f" {self._iteration}."
                )
        else:
            if iteration <= self._iteration:
                raise RuntimeError(
                    f'Port "{port_name}" received a message with iteration'
                    f" {iteration}, but this sub-timeline is already at"
                    f" iteration {self._iteration}."
                )
            self._iteration = iteration
            _reset_participation(self._send_participated, self._receive_participated)

        self._receive_participated.add(key)

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's cycle completes.

        Clears this sub-timeline's iteration, participation state, and leading operator.
        """
        self._iteration = None
        self._first_operator = None
        _reset_participation(self._send_participated, self._receive_participated)

    def get_state(self) -> SubTimelineState:
        """Return this sub-timeline's state, for saving in a snapshot.

        Returns:
            A plain, msgpack-serialisable representation of this
            sub-timeline's iteration, leading operator, and per-port
            participation.
        """
        return {
            "iteration": self._iteration,
            "first_operator": (
                self._first_operator.name if self._first_operator is not None else None
            ),
            "send_participated": list(self._send_participated),
            "receive_participated": list(self._receive_participated),
            "ever_used": self._ever_used,
        }

    def restore_state(self, state: SubTimelineState) -> None:
        """Restore this sub-timeline's state from a snapshot, for snapshot resume.

        Args:
            state: The saved state, as returned by get_state().
        """
        self._iteration = state["iteration"]
        first_operator = state["first_operator"]
        self._first_operator = (
            Operator[first_operator] if first_operator is not None else None
        )
        self._send_participated = {
            (port_name, slot) for port_name, slot in state["send_participated"]
        }
        self._receive_participated = {
            (port_name, slot) for port_name, slot in state["receive_participated"]
        }
        # Older snapshots don't have this key; a snapshot always implies the
        # sub-timeline has an iteration to resume, i.e. it has been used.
        self._ever_used = state.get("ever_used", True)
