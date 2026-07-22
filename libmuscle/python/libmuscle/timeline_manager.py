from dataclasses import dataclass
from typing import Optional, TypedDict

from typing_extensions import TypeAlias
from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager
from libmuscle.util import port_desc

PortAndSlot: TypeAlias = tuple[str, Optional[int]]  # (port_name, slot)
IterationCount: TypeAlias = list[int]  # nested iteration counts of a message


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
    iteration is None if the main timeline has not started yet (or has been reset).
    """

    iteration: Optional[IterationCount]
    send_participated: list[PortAndSlot]
    receive_participated: list[PortAndSlot]
    subtimeline_states: dict[str, SubTimelineState]


class TimelinePorts:
    """Tracks one direction (send or receive) of a (sub-)timeline's ports.

    Records the connected ports of that direction, how many port/slot
    combinations they make up, and which of those have already sent or
    received a message for the current (sub-)iteration.
    """

    def __init__(self, ports: Optional[list[Port]] = None) -> None:
        """Create a TimelinePorts, optionally with its ports already known.

        Args:
            ports: The connected ports of this direction, if known yet.
        """
        self.ports: list[Port] = []
        self.num_slots = 0
        self.participated: set[PortAndSlot] = set()
        if ports is not None:
            self.set_ports(ports)

    def set_ports(self, ports: list[Port]) -> None:
        """Set the connected ports of this direction.

        Args:
            ports: The connected ports of this direction.
        """
        self.ports = ports
        self.num_slots = sum(
            port.get_length() if port.is_vector() else 1 for port in ports
        )

    def participate(self, port_name: str, slot: Optional[int]) -> None:
        """Record that the given port/slot has participated."""
        self.participated.add((port_name, slot))

    def has_participated(self, port_name: str, slot: Optional[int]) -> bool:
        """Return whether the given port/slot has already participated."""
        return (port_name, slot) in self.participated

    def all_participated(self) -> bool:
        """Return whether every port/slot combination has participated."""
        return len(self.participated) == self.num_slots

    def missing_ports(self) -> list[str]:
        """Return descriptions of the port/slot combinations that have not
        participated yet.
        """
        return [
            f'Port "{port_desc(str(port.name), slot)}"'
            for port in self.ports
            for slot in (list(range(port.get_length())) if port.is_vector() else [None])
            if (str(port.name), slot) not in self.participated
        ]

    def reset(self) -> None:
        """Clear participation, keeping the tracked ports."""
        self.participated = set()


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
        self._iteration: Optional[IterationCount] = None
        self._send = TimelinePorts()
        self._receive = TimelinePorts()
        self._submanagers: dict[Timeline, SubTimelineManager] = {}

    def on_ports_connected(self) -> None:
        """Create the SubTimelineManagers once the ports are connected. It also collects
        the main-timeline (F_INIT and O_F) ports and their participation tracking, and
        starts the main timeline at [] right away if it has no F_INIT message to wait
        for.
        """
        all_ports = self._port_manager.list_ports()

        receive_ports = [
            self._port_manager.get_port(name)
            for name in all_ports.get(Operator.F_INIT, [])
            if self._port_manager.get_port(name).is_connected()
        ]
        # muscle_settings_in is F_INIT too, but it's not a declared port, so
        # list_ports() doesn't return it; check_receive/check_received_message
        # do treat it as F_INIT though, so it must be tracked here as well.
        if self._port_manager.settings_in_connected():
            receive_ports.append(self._port_manager.get_port("muscle_settings_in"))
        self._receive.set_ports(receive_ports)

        self._send.set_ports(
            [
                self._port_manager.get_port(name)
                for name in all_ports.get(Operator.O_F, [])
                if self._port_manager.get_port(name).is_connected()
            ]
        )

        subtimelines = self._port_manager.list_subtimelines()

        # Assumes every O_I/S port has a non-empty timeline.
        self._submanagers = {
            tl: SubTimelineManager(tl, self._port_manager) for tl in subtimelines
        }

        # A component with no connected F_INIT ports has no F_INIT message to
        # learn its iteration from, so its main timeline starts at [].
        self._iteration = None if self.has_connected_f_init() else []

    def get_state(self) -> TimelineState:
        """Return the main timeline's iteration and participation, and every
        sub-timeline's state, for saving in a snapshot.
        """
        return TimelineState(
            iteration=self._iteration,
            send_participated=list(self._send.participated),
            receive_participated=list(self._receive.participated),
            subtimeline_states={
                str(tl): stm.get_state() for tl, stm in self._submanagers.items()
            },
        )

    def cycle_complete(self) -> bool:
        """Return whether every main-timeline port has participated and
        every sub-timeline has either completed a sub-iteration or wasn't
        used at all this cycle.
        """
        return (
            self._receive.all_participated()
            and self._send.all_participated()
            and all(stm.is_complete() for stm in self._submanagers.values())
        )

    def finish_cycle(self) -> None:
        """Check if the current timeline cycle has finished and reset for the next one.

        Raises:
            RuntimeError: If the cycle is not complete, i.e. only some of its
                ports have participated. Names exactly which ports haven't sent
                or received a message yet.
        """
        if self.cycle_complete():
            self.reset()
            return

        missing = self._send.missing_ports() + self._receive.missing_ports()
        for stm in self._submanagers.values():
            if not stm.is_complete():
                missing += stm._send.missing_ports() + stm._receive.missing_ports()

        raise RuntimeError(
            "The reuse loop was re-entered, but the previous cycle has not"
            f" completed yet: {', '.join(missing)} did not send or receive a"
            " message. Please make sure every connected port sends or receives a"
            " message before calling reuse_instance() again."
        )

    def has_connected_f_init(self) -> bool:
        """Return whether this component has any connected F_INIT ports,
        including muscle_settings_in."""
        return bool(self._receive.ports)

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
        port = self._port_manager.get_port(port_name)
        assert self._iteration is not None

        if port.operator is Operator.O_F:
            return self._check_send_o_f(port_name, slot)

        return self._submanagers[port.timeline].check_send_message(
            port, slot, self._iteration
        )

    def _check_send_o_f(self, port_name: str, slot: Optional[int]) -> IterationCount:
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
                iteration, or a sub-timeline was used this cycle but hasn't
                completed a sub-iteration.
        """
        assert self._iteration is not None
        if self._send.has_participated(port_name, slot):
            raise RuntimeError(
                f'Port "{port_desc(port_name, slot)}" already sent a message for this'
                " iteration."
            )

        for tl, stm in self._submanagers.items():
            if not stm.is_complete():
                missing = stm._send.missing_ports() + stm._receive.missing_ports()
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" tried to send a message, but'
                    f" sub-timeline {tl} has not completed a sub-iteration yet."
                    f" Missing: {', '.join(missing)}."
                )

        self._send.participate(port_name, slot)
        return self._iteration

    def restore_state(self, state: TimelineState) -> None:
        """Restore the main timeline and every sub-timeline, for snapshot resume.

        Restores the main timeline's iteration and per-port participation, and every
        sub-timeline's state, from the snapshot.

        Args:
            state: The saved timeline state, as returned by get_state().
        """
        self._iteration = state.iteration
        self._send.participated = set(state.send_participated)
        self._receive.participated = set(state.receive_participated)
        for tl, stm in self._submanagers.items():
            sub_state = state.subtimeline_states.get(str(tl))
            if sub_state is not None:
                stm.restore_state(sub_state)

    def check_receive(self, port_name: str, slot: Optional[int] = None) -> None:
        """Check that receiving on the given port is currently allowed.

        An F_INIT port may always receive before the main timeline has
        started, and afterwards may receive again as long as it has not
        already received a message for the current iteration.

        Whether an S port may receive is delegated to the corresponding
        SubTimelineManager.

        Args:
            port_name: Name of the F_INIT or S port about to receive.
            slot: The slot being received on, if this is a vector port.
        """
        port = self._port_manager.get_port(port_name)

        if port.operator is Operator.F_INIT:
            if self._receive.has_participated(port_name, slot):
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" already received a message'
                    " for this iteration."
                )
            return

        if port.operator is Operator.S:
            self._submanagers[port.timeline].check_receive(port, slot)

    def check_received_message(
        self,
        port_name: str,
        slot: Optional[int],
        iteration: IterationCount,
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
            slot: The slot the message was received on, if this is a vector
                port.
            iteration: The iteration the received message was sent with.

        Raises:
            RuntimeError: If an F_INIT port received a message with an
                iteration different from the one the main timeline is on.
        """
        port = self._port_manager.get_port(port_name)

        if port.operator is Operator.F_INIT:
            if self._iteration is None:
                self._iteration = iteration
            elif iteration != self._iteration:
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" received a message with'
                    f" iteration {iteration}, but the main timeline is at"
                    f" iteration {self._iteration}."
                )
            self._receive.participate(port_name, slot)
            return

        self._submanagers[port.timeline].check_received_message(
            port_name, slot, iteration
        )

    def reset(self) -> None:
        """Reset the main timeline and it's sub-timelines.

        Clears the main timeline's iteration (back to [] if there are no connected
        F_INIT ports to wait for) and participation state, and resets every sub-timeline
        in turn.
        """
        self._iteration = None if self.has_connected_f_init() else []
        self._send.reset()
        self._receive.reset()
        for stm in self._submanagers.values():
            stm.reset()


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

        timeline_ports = port_manager.list_ports(timeline)
        self._send = TimelinePorts(
            [
                port_manager.get_port(name)
                for name in timeline_ports.get(Operator.O_I, [])
                if port_manager.get_port(name).is_connected()
            ]
        )
        self._receive = TimelinePorts(
            [
                port_manager.get_port(name)
                for name in timeline_ports.get(Operator.S, [])
                if port_manager.get_port(name).is_connected()
            ]
        )

    def is_complete(self) -> bool:
        """Return whether this sub-timeline is done with this cycle.

        If it was used this cycle, every one of its ports must have
        participated. If it wasn't used this cycle, that's fine: a
        sub-timeline may be skipped entirely, e.g. a component going
        straight from F_INIT to O_F without ever using its O_I/S ports, or a
        cache skipping a refresh on some cycles.
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

        Raises:
            RuntimeError: If this port and slot has not yet sent a message
                for the current sub-iteration and S led this sub-timeline
                with only some, not all, of its S ports having received yet;
                or if it already sent one and either S led this sub-timeline
                (only a receive on S may advance it) or not every port of
                this sub-timeline has participated yet.
        """
        port_name = str(port.name)

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
            self._first_operator = Operator.O_I
        elif not self._send.has_participated(port_name, slot):
            if self._first_operator is Operator.S and not (
                self._receive.all_participated()
            ):
                missing = self._receive.missing_ports()
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" tried to send a message, but'
                    " only some of this sub-timeline's S ports have received so"
                    f" far. Missing: {', '.join(missing)}."
                )
        else:
            if self._first_operator is not Operator.O_I:
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" tried to send a message, but'
                    " S received first on this sub-timeline, so only a receive on S"
                    " can advance to the next sub-iteration, not a send on O_I."
                )
            if not (self._send.all_participated() and self._receive.all_participated()):
                missing = self._send.missing_ports() + self._receive.missing_ports()
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" tried to send a message, but'
                    " it already sent one for this sub-iteration and not every port of"
                    f" this sub-timeline has participated yet. Missing:"
                    f" {', '.join(missing)}."
                )
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

        Raises:
            RuntimeError: If this S port has not yet received for the
                current sub-iteration and only some, not all, of this
                sub-timeline's O_I ports have sent so far; or if it already
                received for the current sub-iteration and either O_I led
                this sub-timeline (only a send on O_I may advance it), or
                not every port of this sub-timeline has participated yet.
        """
        port_name = str(port.name)

        if not self._receive.has_participated(port_name, slot):
            if self._first_operator is Operator.O_I and not (
                self._send.all_participated()
            ):
                missing = self._send.missing_ports()
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" tried to receive a message,'
                    " but only some of this sub-timeline's O_I ports have sent so far."
                    f" Missing: {', '.join(missing)}."
                )
            return

        if self._first_operator is not Operator.S:
            raise RuntimeError(
                f'Port "{port_desc(port_name, slot)}" tried to receive a message, but'
                " O_I sent first on this sub-timeline, so only a send on O_I can"
                " advance to the next sub-iteration, not a receive on S."
            )
        if not (self._send.all_participated() and self._receive.all_participated()):
            missing = self._send.missing_ports() + self._receive.missing_ports()
            raise RuntimeError(
                f'Port "{port_desc(port_name, slot)}" tried to receive a message, but'
                " it already received one for this sub-iteration and not every port of"
                f" this sub-timeline has participated yet. Missing:"
                f" {', '.join(missing)}."
            )

    def check_received_message(
        self, port_name: str, slot: Optional[int], iteration: IterationCount
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
        if self._iteration is None:
            self._iteration = iteration
            self._first_operator = Operator.S
        elif not self._receive.has_participated(port_name, slot):
            if iteration != self._iteration:
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" received a message with'
                    f" iteration {iteration}, but this sub-timeline is at"
                    f" iteration {self._iteration}."
                )
        else:
            if iteration <= self._iteration:
                raise RuntimeError(
                    f'Port "{port_desc(port_name, slot)}" received a message with'
                    f" iteration {iteration}, but this sub-timeline is already at"
                    f" iteration {self._iteration}."
                )
            self._iteration = iteration
            self._send.reset()
            self._receive.reset()

        self._receive.participate(port_name, slot)

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's cycle completes.

        Clears this sub-timeline's iteration, participation state, and leading operator.
        """
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
        return {
            "iteration": self._iteration,
            "first_operator": (
                self._first_operator.name if self._first_operator is not None else None
            ),
            "send_participated": list(self._send.participated),
            "receive_participated": list(self._receive.participated),
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
        self._send.participated = set(state["send_participated"])
        self._receive.participated = set(state["receive_participated"])
