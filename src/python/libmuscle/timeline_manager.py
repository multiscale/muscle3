from dataclasses import dataclass
from typing import Optional, TypedDict

from typing_extensions import TypeAlias
from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager
from libmuscle.util import port_desc

PortAndSlot: TypeAlias = tuple[str, Optional[int]]  # (port_name, slot)
IterationCount: TypeAlias = list[int]  # nested iteration counts of a message
ExpectedActions: TypeAlias = list[tuple[str, Port, list[int]]]


def is_subiteration_or_equal(it1: IterationCount, it2: IterationCount) -> bool:
    """Check if it1 is a subiteration of it2, or if both counts are equal.

    Example:
        `[1, 2, 3]` is a subiteration of `[1, 2]`, `[1]` and `[]`, but not of `[0]`.
    """
    return it1[: len(it2)] == it2


def get_most_nested_iteration(iterations: list[IterationCount]) -> IterationCount:
    """Return the most nested iteration in the list, i.e. the one with the most items.

    Raises:
        ValueError if iterations is an empty list or if the iterations are incompatible
        with one another.

    Example:
        >>> get_most_nested_iteration([[1, 2, 3], [1], [1, 2, 3, 4]])
        [1, 2, 3, 4]
        >>> get_most_nested_iteration([[1], [2], [1, 2, 3, 4]])
        ValueError("[1, 2, 3, 4] is not a subiteration of [2]")
    """
    if not iterations:
        raise ValueError("iterations is an empty list")
    iterations.sort()
    for i in range(len(iterations) - 1):
        if not is_subiteration_or_equal(iterations[i + 1], iterations[i]):
            raise ValueError(
                f"{iterations[i + 1]} is not a subiteration of {iterations[i]}"
            )
    return iterations[-1]


class SubTimelineState(TypedDict):
    """A single sub-timeline's state, as returned by
    SubTimelineManager.get_state() for saving in a snapshot."""

    iteration: Optional[IterationCount]
    first_operator: Optional[str]
    send_participated: list[PortAndSlot]
    receive_participated: list[PortAndSlot]


@dataclass
class TimelineState:
    """The main timeline's iteration and participation, and every
    sub-timeline's state.

    Returned by TimelineManager.get_state() for saving in a snapshot, and
    passed back into TimelineManager.restore_state() to resume from one.
    iteration is None if the main timeline has not started yet.
    """

    iteration: Optional[IterationCount]
    send_participated: list[PortAndSlot]
    subtimeline_states: dict[str, SubTimelineState]


def _port_ref(port: Port, slots: list[int]) -> str:
    """Format e.g. "O_F port 'x'", "O_I port 'x[3]'", or "S port 'y'
    (slots 2, 3, 5)"."""
    if not slots:
        return f"{port.operator.name} port '{port.name}'"
    if len(slots) == 1:
        return f"{port.operator.name} port '{port_desc(str(port.name), slots[0])}'"
    slot_list = ", ".join(str(slot) for slot in slots)
    return f"{port.operator.name} port '{port.name}' (slots {slot_list})"


def _expected_message(subject: str, expected: ExpectedActions) -> str:
    bullets = "\n".join(
        f"- A {action} on {_port_ref(port, slots)}" for action, port, slots in expected
    )
    return (
        f"Not allowed to {subject} yet: was expecting one of the following"
        f" instead:\n{bullets}"
    )


class TimelineError(RuntimeError):
    """Base class for exceptions raised when Instance's send/receive calls
    violate the timeline consistency rules."""


class PortBlocked(TimelineError):
    """The given port cannot send/receive yet: other ports must send or
    receive a message first."""

    def __init__(
        self, port: Port, slot: Optional[int], expected: ExpectedActions
    ) -> None:
        self.action = "send" if port.operator.allows_sending() else "receive"
        self.port = port
        self.slot = slot
        self.expected = expected
        slots = [slot] if slot is not None else []
        subject = f"{self.action} a message on {_port_ref(port, slots)}"
        super().__init__(_expected_message(subject, expected))


class ReuseLoopIncomplete(TimelineError):
    """reuse_instance() was called before the previous reuse loop iteration finished."""

    def __init__(self, expected: ExpectedActions) -> None:
        self.expected = expected
        super().__init__(_expected_message("call reuse_instance()", expected))


class AlreadyParticipated(TimelineError):
    """The given port already sent/received a message this reuse loop
    iteration."""

    def __init__(self, port: Port, slot: Optional[int]) -> None:
        self.action = "send" if port.operator.allows_sending() else "receive"
        self.port = port
        self.slot = slot
        done = "sent" if self.action == "send" else "received"
        slots = [slot] if slot is not None else []
        super().__init__(
            f"Not allowed to {self.action} another message on"
            f" {_port_ref(port, slots)} yet: it already {done} one this"
            f" reuse loop iteration."
        )


class MessageOutOfSync(TimelineError):
    """A received message doesn't belong where this component expects it.

    The timeline manager's bookkeeping should never let this state be reached. Seeing
    this means there is probably a bug in MUSCLE3."""

    def __init__(self, port: Port, slot: Optional[int]) -> None:
        self.port = port
        self.slot = slot
        slots = [slot] if slot is not None else []
        super().__init__(
            f"Received a message on {_port_ref(port, slots)} that this"
            " component wasn't expecting. This should not happen and may be"
            " a bug in MUSCLE3. Please file an issue at"
            " https://github.com/multiscale/muscle3/issues."
        )


class TimelinePorts:
    """Tracks one direction (send or receive) of a (sub-)timeline's ports.

    Records the connected ports of that direction, how many port/slot
    combinations they make up, and which of those have already sent or
    received a message for the current (sub-)iteration.
    """

    def __init__(self, ports: list[Port]) -> None:
        self.ports = ports
        self.participated: set[PortAndSlot] = set()

    def participate(self, port_name: str, slot: Optional[int]) -> None:
        """Record that the given port/slot has participated."""
        self.participated.add((port_name, slot))

    def has_participated(self, port_name: str, slot: Optional[int]) -> bool:
        """Return whether the given port/slot has already participated."""
        return (port_name, slot) in self.participated

    def all_participated(self) -> bool:
        """Return whether every port/slot combination has participated."""
        num = sum(port.get_length() if port.is_vector() else 1 for port in self.ports)
        return len(self.participated) == num

    def missing_ports(self) -> list[tuple[Port, list[int]]]:
        """Return each connected port that still has slots which haven't
        participated yet, paired with the list of those slots ([] for a
        scalar port).
        """
        result = []
        for port in self.ports:
            if port.is_vector():
                slots = [
                    slot
                    for slot in range(port.get_length())
                    if (str(port.name), slot) not in self.participated
                ]
                if slots:
                    result.append((port, slots))
            elif (str(port.name), None) not in self.participated:
                result.append((port, []))
        return result

    def all_ports(self) -> list[tuple[Port, list[int]]]:
        """Return every connected port together with all of its slots
        ([] for a scalar port), regardless of participation.
        """
        result = []
        for port in self.ports:
            slots = list(range(port.get_length())) if port.is_vector() else []
            result.append((port, slots))
        return result

    def reset(self) -> None:
        """Clear participation, keeping the tracked ports."""
        self.participated = set()


def _expected_actions(
    send: Optional[TimelinePorts] = None,
    receive: Optional[TimelinePorts] = None,
    *,
    missing_only: bool = True,
) -> ExpectedActions:
    """The expected next actions on a send/receive pair of TimelinePorts in the order
    defined by the TimelineManager.

    Pass only send or only receive when the other direction isn't relevant to the
    check being made. Pass missing_only=False to list every port on the given side(s)
    instead of just the ones that haven't participated yet.
    """
    result: ExpectedActions = []
    if send is not None:
        ports = send.missing_ports() if missing_only else send.all_ports()
        result += [("send", port, slots) for port, slots in ports]
    if receive is not None:
        ports = receive.missing_ports() if missing_only else receive.all_ports()
        result += [("receive", port, slots) for port, slots in ports]
    return result


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

        The port_manager must already have its ports connected to their peers, since
        this collects the main-timeline (F_INIT and O_F) ports with it's
        SubTimelineManagers, and starts the main timeline at [] right away if it has no
        F_INIT message to wait for.

        Args:
            port_manager: The (already connected) port manager for this instance.
        """
        self._port_manager = port_manager
        self._send = TimelinePorts(port_manager.get_connected_ports(Operator.O_F))
        subtimelines = port_manager.list_subtimelines()
        self._submanagers = {
            tl: SubTimelineManager(tl, self._port_manager) for tl in subtimelines
        }
        self._iteration: Optional[IterationCount] = None
        """Current component iteration count. Is None before the first reuse loop."""

    def get_iteration(self) -> IterationCount:
        """Get the current component iteration count."""
        assert self._iteration is not None
        return self._iteration

    def check_send_message(
        self, port_name: str, slot: Optional[int] = None
    ) -> IterationCount:
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
        assert self._iteration is not None
        port = self._port_manager.get_port(port_name)

        if port.operator is Operator.O_F:
            return self._check_send_o_f(port, slot)

        return self._submanagers[port.timeline].check_send_message(
            port, slot, self._iteration
        )

    def check_pre_received_iteration_counts(
        self, iterations: list[IterationCount]
    ) -> IterationCount:
        """Check if the iteration counts of pre-received messages are consistent.

        Returns:
            The iteration count for the upcoming reuse loop.

        Raises:
            ValueError if the iteration counts are inconsistent.
        """
        if not iterations:
            assert not self._port_manager.has_f_init_connections()
            new_iteration = []
        else:
            new_iteration = get_most_nested_iteration(iterations)
        if self._iteration is not None and new_iteration <= self._iteration:
            raise RuntimeError(
                f"Internal error: received F_INIT iteration count {new_iteration} "
                f"is not newer than the previous iteration {self._iteration}."
            )
        self._iteration = new_iteration
        return self._iteration

    def _check_send_o_f(self, port: Port, slot: Optional[int]) -> IterationCount:
        """Check the O_F-specific send conditions, update state, and return
        the iteration to embed in the outgoing message.

        An O_F port requires that it has not already sent for the current iteration and
        that every sub-timeline has either completed a sub-iteration or wasn't used at
        all this iteration.

        Args:
            port: The O_F port that is about to send.
            slot: The slot being sent on, if this is a vector port.

        Returns:
            The iteration to embed in the outgoing message.
        """
        assert self._iteration is not None
        port_name = str(port.name)
        # Sending on O_F is only allowed when all subtimelines have completed an
        # iteration:
        expected: ExpectedActions = []
        for stm in self._submanagers.values():
            if not stm.is_complete():
                expected += _expected_actions(stm._send, stm._receive)
        if expected:
            raise PortBlocked(port, slot, expected)

        # Cannot send twice in the same reuse-loop iteration
        if self._send.has_participated(port_name, slot):
            raise AlreadyParticipated(port, slot)
        self._send.participate(port_name, slot)

        return self._iteration

    def check_receive_s(self, port_name: str, slot: Optional[int] = None) -> None:
        """Check that receiving on the given S port is currently allowed.

        Args:
            port_name: Name of the S port about to receive.
            slot: The slot being received on, if this is a vector port.
        """
        port = self._port_manager.get_port(port_name)
        assert port.operator is Operator.S
        self._submanagers[port.timeline].check_receive(port, slot)

    def record_received_s_message(
        self,
        port_name: str,
        slot: Optional[int],
        iteration: IterationCount,
        num_repeat_filters: int = 0,
    ) -> IterationCount:
        """Record that a message has been received on the given S port.

        check_receive_s already established that this receive is allowed.

        Args:
            port_name: Name of the S port a message was received on.
            slot: The slot the message was received on, if this is a vector port.
            iteration: The iteration the received message was sent with.
            num_repeat_filters: Number of repeat filters applied to this S port.

        Returns:
            New iteration count for the subtimeline of the S port.
        """
        port = self._port_manager.get_port(port_name)
        assert port.operator is Operator.S
        assert self._iteration is not None
        return self._submanagers[port.timeline].record_received_message(
            port, slot, iteration, self._iteration, num_repeat_filters
        )

    def reset(self) -> None:
        """Reset the main timeline and it's sub-timelines.

        Clears the main timeline's iteration (back to [] if there are no connected
        F_INIT ports to wait for) and participation state, and resets every sub-timeline
        in turn.
        """
        self._send.reset()
        for stm in self._submanagers.values():
            stm.reset()

    def start_reuse_iteration(self) -> Optional[IterationCount]:
        """Called at the start of the reuse loop.

        If this is not the first run, checks if the previous reuse loop is complete:
        The reuse loop iteration is complete once every main-timeline port has
        participated and every sub-timeline has either completed a sub-iteration or
        wasn't used at all this reuse loop iteration.

        Returns:
            Iteration count of the finished reuse loop or None if this is the first run.
        """
        iteration = self._iteration
        if iteration is None or (
            self._send.all_participated()
            and all(stm.is_complete() for stm in self._submanagers.values())
        ):
            self.reset()
            return iteration

        expected = _expected_actions(self._send)
        for stm in self._submanagers.values():
            if not stm.is_complete():
                expected += _expected_actions(stm._send, stm._receive)

        raise ReuseLoopIncomplete(expected)

    def get_state(self) -> TimelineState:
        """Return the main timeline's iteration and participation, and every
        sub-timeline's state, for saving in a snapshot.
        """
        # N.B. we only sort send/receive participated to test equality.
        return TimelineState(
            iteration=self._iteration,
            send_participated=sorted(self._send.participated),
            subtimeline_states={
                str(tl): stm.get_state() for tl, stm in self._submanagers.items()
            },
        )

    def restore_state(self, state: TimelineState) -> None:
        """Restore the main timeline and every sub-timeline, for snapshot resume.

        Restores the main timeline's iteration and per-port participation, and every
        sub-timeline's state, from the snapshot.

        Args:
            state: The saved timeline state, as returned by get_state().
        """
        self._iteration = state.iteration
        self._send.participated = {(p, s) for p, s in state.send_participated}
        for tl, stm in self._submanagers.items():
            sub_state = state.subtimeline_states.get(str(tl))
            if sub_state is not None:
                stm.restore_state(sub_state)


class SubTimelineManager:
    """Tracks iteration state for a single sub-timeline."""

    def __init__(self, timeline: Timeline, port_manager: PortManager) -> None:
        """Create a SubTimelineManager.

        Args:
            timeline: The timeline this manager tracks.
            port_manager: The port manager; used to look up the O_I and S ports
                belonging to this sub-timeline.
        """
        self._timeline = timeline
        self._iteration: Optional[IterationCount] = None
        self._first_operator: Optional[Operator] = None

        self._send = TimelinePorts(
            port_manager.get_connected_ports(Operator.O_I, timeline)
        )
        self._receive = TimelinePorts(
            port_manager.get_connected_ports(Operator.S, timeline)
        )

    def is_complete(self) -> bool:
        """Return whether this sub-timeline is done with this reuse loop iteration.

        If it was used this reuse loop iteration, every one of its ports must
        have participated. If it wasn't used this reuse loop iteration,
        that's fine: a sub-timeline may be skipped entirely, e.g. a component
        going straight from F_INIT to O_F without ever using its O_I/S ports,
        or a cache skipping a refresh on some reuse loop iterations.
        """
        if self._iteration is not None:
            return self._send.all_participated() and self._receive.all_participated()
        return True

    def check_send_message(
        self, port: Port, slot: Optional[int], parent_iteration: IterationCount
    ) -> IterationCount:
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
        """
        port_name = str(port.name)

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
            self._first_operator = Operator.O_I
        elif not self._send.has_participated(port_name, slot):
            if self._first_operator is Operator.S and not (
                self._receive.all_participated()
            ):
                expected = _expected_actions(receive=self._receive)
                raise PortBlocked(port, slot, expected)
        else:
            if self._first_operator is not Operator.O_I:
                expected = _expected_actions(receive=self._receive, missing_only=False)
                raise PortBlocked(port, slot, expected)
            if not self.is_complete():
                expected = _expected_actions(self._send, self._receive)
                raise PortBlocked(port, slot, expected)
            self._iteration[-1] += 1
            self._send.reset()
            self._receive.reset()

        self._send.participate(port_name, slot)
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
        """
        port_name = str(port.name)

        if not self._receive.has_participated(port_name, slot):
            if self._first_operator is Operator.O_I and not (
                self._send.all_participated()
            ):
                expected = _expected_actions(send=self._send)
                raise PortBlocked(port, slot, expected)
        else:
            if self._first_operator is not Operator.S:
                expected = _expected_actions(send=self._send, missing_only=False)
                raise PortBlocked(port, slot, expected)
            if not (self._send.all_participated() and self._receive.all_participated()):
                expected = _expected_actions(self._send, self._receive)
                raise PortBlocked(port, slot, expected)

    def record_received_message(
        self,
        port: Port,
        slot: Optional[int],
        iteration: IterationCount,
        component_iteration: IterationCount,
        num_repeat_filters: int,
    ) -> IterationCount:
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
            port: The S port a message was received on.
            slot: The slot the message was received on, if this is a vector port.
            iteration: The iteration the received message was sent with.
            component_iteration: The current iteration of the component.
            num_repeat_filters: Number of repeater filters applied to this message.

        Returns:
            Current iteration count of the subtimeline.

        Raises:
            MessageOutOfSync: If this port and slot has not yet received for
                the current sub-iteration and the message's iteration does
                not match this sub-timeline's current iteration; or if it
                already received for the current sub-iteration and the
                message's iteration is not strictly later than the current
                one.
        """
        port_name = str(port.name)

        if self._iteration is None:
            if num_repeat_filters > 0:
                # Handle cases with multiple levels of repeat filters, for example:
                # - cached message iteration count: [2], with 2 repeat filters
                # - component iteration count: [2, 1]
                # Our iteration count needs to become [2, 1, 0]
                iteration = component_iteration + [0]
            self._iteration = iteration
            self._first_operator = Operator.S
        elif not self._receive.has_participated(port_name, slot):
            if num_repeat_filters == 0 and iteration != self._iteration:
                raise MessageOutOfSync(port, slot)
        else:
            if num_repeat_filters:
                self._iteration[-1] += 1
            elif iteration <= self._iteration:
                raise MessageOutOfSync(port, slot)
            else:
                self._iteration = iteration
            self._send.reset()
            self._receive.reset()

        self._receive.participate(port_name, slot)
        return self._iteration

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's reuse loop iteration
        completes."""
        self._iteration = None
        self._first_operator = None
        self._send.reset()
        self._receive.reset()

    def get_state(self) -> SubTimelineState:
        """Return this sub-timeline's state, for saving in a snapshot.

        Returns:
            A plain, msgpack-serialisable representation of this
            sub-timeline's iteration, leading operator, and per-port
            participation.
        """
        # N.B. we only sort send/receive participated to test equality.
        return {
            "iteration": self._iteration,
            "first_operator": (
                self._first_operator.name if self._first_operator is not None else None
            ),
            "send_participated": sorted(self._send.participated),
            "receive_participated": sorted(self._receive.participated),
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
        self._send.participated = {(p, s) for p, s in state["send_participated"]}
        self._receive.participated = {(p, s) for p, s in state["receive_participated"]}
