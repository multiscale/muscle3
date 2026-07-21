import logging
from dataclasses import dataclass
from typing import Any, Optional

from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager

_logger = logging.getLogger(__name__)


@dataclass
class TimelineState:
    """The main timeline's iteration and participation, and every
    sub-timeline's state.

    Returned by TimelineManager.get_state() for saving in a snapshot, and
    passed back into TimelineManager.restore_state() to resume from one.
    """

    iteration: list[int]
    # Every main-timeline (F_INIT/O_F) port and slot's participation, as
    # [port_name, slot, participated] triples (msgpack cannot serialize the
    # (port_name, slot) tuple keys TimelineManager itself uses as a dict key).
    participated: list[list[Any]]
    sub_timeline_states: dict[str, dict[str, Any]]


def _slots(port: Port) -> list[Optional[int]]:
    """Return the slot indices of a port, or [None] if it's scalar."""
    if port.is_vector():
        return list(range(port.get_length()))
    return [None]


def _all_ports_participated(
    ports: list[Port],
    participated: dict[tuple[str, Optional[int]], bool],
    operator: Optional[Operator] = None,
) -> bool:
    """Return True if every matching port has participated in the current iteration.

    For a vector port, every one of its slots must have participated.

    Args:
        ports: All ports sharing the same (sub)timeline.
        participated: Whether each port and slot, keyed by (name, slot), has
            sent or received a message for the current iteration.
        operator: If given, only ports with this operator are considered;
            otherwise every port in ports is considered.

    Returns:
        True if every matching port (and every slot of it) has participated.
    """
    return all(
        participated.get((str(port.name), slot), False)
        for port in ports
        if operator is None or port.operator == operator
        for slot in _slots(port)
    )


def _reset_participation(participated: dict[tuple[str, Optional[int]], bool]) -> None:
    """Mark every port and slot as not yet participated, reset all to False.

    Args:
        participated: Whether each port and slot, keyed by (name, slot), has
            sent or received a message for the current iteration.
    """
    for key in participated:
        participated[key] = False


def _sub_timeline_complete(stm: "SubTimelineManager") -> bool:
    """Return whether a sub-timeline is done with this cycle: either it was
    never used this cycle, or every one of its ports has participated.
    """
    return stm._iteration is None or _all_ports_participated(
        stm._ports, stm._participated
    )


class TimelineManager:
    """Tracks iteration state for the main timeline and manages it's sub-timelines.

    O_F and F_INIT ports live on the main timeline, tracked directly by this manager.
    O_I and S ports live on sub-timelines, each tracked by its own SubTimelineManager,
    grouped by the port's timeline attribute.

    Every TimelineManager and SubTimelineManager records, for each of its
    ports, whether that port has already sent or received a message for the
    current iteration, in a dict of booleans keyed by port name.
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
        self._ports: list[Port] = []
        self._participated: dict[tuple[str, Optional[int]], bool] = {}
        self._sub_timelines: dict[Timeline, SubTimelineManager] = {}

    def connect_sub_timelines(self) -> None:
        """Create the SubTimelineManagers once the ports are connected. It also collects
        the main-timeline (F_INIT and O_F) ports and their participation tracking, and
        starts the main timeline at [] right away if it has no F_INIT message to wait
        for.
        """
        all_ports = self._port_manager.list_ports()

        # TODO: Which checks should hold for the Operator.NONE?
        if any(
            self._port_manager.get_port(name).is_connected()
            for name in all_ports.get(Operator.NONE, [])
        ):
            _logger.warning(
                "This instance is using ports with Operator.NONE. This does not "
                "adhere to the Multiscale Modelling and Simulation Framework "
                "and may lead to deadlocks."
            )

        self._ports = [
            self._port_manager.get_port(name)
            for op in (Operator.F_INIT, Operator.O_F)
            for name in all_ports.get(op, [])
            if self._port_manager.get_port(name).is_connected()
        ]
        self._participated = {
            (str(port.name), slot): False
            for port in self._ports
            for slot in _slots(port)
        }

        sub_timelines = {
            self._port_manager.get_port(name).timeline
            for op in (Operator.O_I, Operator.S)
            for name in all_ports.get(op, [])
            if self._port_manager.get_port(name).is_connected()
        }

        # Assumes every O_I/S port has a non-empty timeline.
        self._sub_timelines = {
            tl: SubTimelineManager(tl, self._port_manager) for tl in sub_timelines
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
            participated=[
                [port_name, slot, participated]
                for (port_name, slot), participated in self._participated.items()
            ],
            sub_timeline_states={
                str(tl): stm.get_state() for tl, stm in self._sub_timelines.items()
            },
        )

    def cycle_complete(self) -> bool:
        """Return whether every main-timeline port has participated and
        every sub-timeline has either completed a sub-iteration or wasn't
        used at all this cycle.
        """
        return _all_ports_participated(self._ports, self._participated) and all(
            _sub_timeline_complete(stm) for stm in self._sub_timelines.values()
        )

    def _has_connected_f_init(self) -> bool:
        """Return whether this component has any connected F_INIT ports."""
        return any(
            p.is_connected() for p in self._ports if p.operator == Operator.F_INIT
        )

    def check_send_message(
        self, port_name: str, slot: Optional[int] = None
    ) -> list[int]:
        """Check and update the timeline state before sending on the given port.

        Both O_F and O_I require that all F_INIT ports should have received a message
        for the current iteration. After this the specific checks for the O_F or O_I
        port will be done and the iteration of it's timeline will be returned.

        Args:
            port_name: Name of the O_F or O_I port that is about to send.
            slot: The slot being sent on, if this is a vector port.

        Returns:
            The iteration to embed in the outgoing message.

        Raises:
            RuntimeError: If sending on this port at this point would violate
                the Multiscale Modeling and Simulation Framework.
        """
        port = self._port_manager.get_port(port_name)

        if self._iteration is None:
            raise RuntimeError(
                f'Port "{port_name}" tried to send a message, but this'
                " component has connected F_INIT ports and must receive on"
                " all of them first."
            )
        if not _all_ports_participated(
            self._ports, self._participated, Operator.F_INIT
        ):
            raise RuntimeError(
                f'Port "{port_name}" tried to send a message, but not all'
                " F_INIT ports have received a message for this iteration yet."
            )

        if port.operator == Operator.O_F:
            return self._check_send_o_f(port_name, slot)

        return self._sub_timelines[port.timeline].check_send_message(
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
        assert self._iteration is not None, "checked by _check_main_timeline_started"
        if self._participated.get((port_name, slot), False):
            raise RuntimeError(
                f'Port "{port_name}" already sent a message for this iteration.'
            )

        for stm in self._sub_timelines.values():
            if not _sub_timeline_complete(stm):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but a'
                    " sub-timeline has not completed a sub-iteration yet."
                )

        self._participated[(port_name, slot)] = True
        return self._iteration

    def restore_state(self, state: Optional[TimelineState]) -> None:
        """Restore the main timeline and every sub-timeline, for snapshot resume.

        Resets everything first, then restores the main timeline's iteration, per-port
        participation, and every sub-timeline's state from the snapshot.

        If no state was given, there is no participation record to restore, so every
        F_INIT port and slot is instead marked as participated.

        Args:
            state: The saved timeline state, as returned by get_state(), or
                None if the snapshot was saved by an older version of MUSCLE3.

        Raises:
            RuntimeError: If no state was given while this component has connected
                F_INIT ports, so there is no recorded iteration to resume from and this
                snapshot cannot be resumed correctly.
        """
        self.reset()
        if state is None and self._iteration is None:
            raise RuntimeError(
                "Resuming from an intermediate snapshot, but it does not"
                " record the timeline iteration F_INIT was received at,"
                " even though this component has connected F_INIT ports."
                " This snapshot cannot be resumed correctly."
            )

        if state is None:
            for port in self._ports:
                if port.operator == Operator.F_INIT:
                    for slot in _slots(port):
                        self._participated[(str(port.name), slot)] = True
            return

        self._iteration = state.iteration
        self._participated = {
            (port_name, slot): participated
            for port_name, slot, participated in state.participated
        }
        for tl, stm in self._sub_timelines.items():
            sub_state = state.sub_timeline_states.get(str(tl))
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

        if port.operator == Operator.F_INIT:
            if self._participated.get((port_name, slot), False):
                raise RuntimeError(
                    f'Port "{port_name}" already received a message for this iteration.'
                )
            return

        if port.operator == Operator.S:
            if self._iteration is None:
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive the first message,'
                    " but this component has connected F_INIT ports and must"
                    " receive on all of them first."
                )
            if not _all_ports_participated(
                self._ports, self._participated, Operator.F_INIT
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            self._sub_timelines[port.timeline].check_receive(port, slot)
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

        if port.operator == Operator.F_INIT:
            if self._iteration is None:
                self._iteration = iteration
            elif iteration != self._iteration:
                raise RuntimeError(
                    f'Port "{port_name}" received a message with iteration'
                    f" {iteration}, but the main timeline is at iteration"
                    f" {self._iteration}."
                )
            self._participated[(port_name, slot)] = True
            return

        self._sub_timelines[port.timeline].check_received_message(
            port_name, slot, iteration
        )

    def reset(self) -> None:
        """Reset the main timeline and it's sub-timelines.

        Clears the main timeline's iteration (back to [] if there are no connected
        F_INIT ports to wait for) and participation state, and resets every sub-timeline
        in turn.
        """
        self._iteration = None if self._has_connected_f_init() else []
        _reset_participation(self._participated)
        for stm in self._sub_timelines.values():
            stm.reset()


class SubTimelineManager:
    """Tracks iteration state for a single sub-timeline."""

    def __init__(
        self, sub_timeline: Optional[Timeline], port_manager: PortManager
    ) -> None:
        """Create a SubTimelineManager.

        Args:
            sub_timeline: The timeline this manager tracks.
            port_manager: The port manager; used to look up the O_I and S ports
                belonging to this sub-timeline.
        """
        self._sub_timeline = sub_timeline
        self._iteration: Optional[list[int]] = None
        self._first_operator: Optional[Operator] = None

        self._ports = [
            port_manager.get_port(name)
            for op in (Operator.O_I, Operator.S)
            for name in port_manager.list_ports(sub_timeline).get(op, [])
            if port_manager.get_port(name).is_connected()
        ]
        self._participated = {
            (str(port.name), slot): False
            for port in self._ports
            for slot in _slots(port)
        }

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

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
            self._first_operator = Operator.O_I
        elif not self._participated.get(key, False):
            if self._first_operator == Operator.S and not _all_ports_participated(
                self._ports, self._participated, Operator.S
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but only'
                    " some of this sub-timeline's S ports have received so far."
                )
        else:
            if self._first_operator != Operator.O_I:
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but S received'
                    " first on this sub-timeline, so only a receive on S can"
                    " advance to the next sub-iteration, not a send on O_I."
                )
            if not _all_ports_participated(self._ports, self._participated):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but it already'
                    " sent one for this sub-iteration and not every port of this"
                    " sub-timeline has participated yet."
                )
            self._iteration[-1] += 1
            _reset_participation(self._participated)

        self._participated[key] = True
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

        if not self._participated.get((port_name, slot), False):
            if self._first_operator == Operator.O_I and not _all_ports_participated(
                self._ports, self._participated, Operator.O_I
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive a message, but only'
                    " some of this sub-timeline's O_I ports have sent so far."
                )
            return

        if self._first_operator != Operator.S:
            raise RuntimeError(
                f'Port "{port_name}" tried to receive a message, but O_I sent'
                " first on this sub-timeline, so only a send on O_I can"
                " advance to the next sub-iteration, not a receive on S."
            )
        if not _all_ports_participated(self._ports, self._participated):
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

        if self._iteration is None:
            self._iteration = iteration
            self._first_operator = Operator.S
        elif not self._participated.get(key, False):
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
            _reset_participation(self._participated)

        self._participated[key] = True

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's cycle completes.

        Clears this sub-timeline's iteration, participation state, and leading operator.
        """
        self._iteration = None
        self._first_operator = None
        _reset_participation(self._participated)

    def get_state(self) -> dict[str, Any]:
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
            "participated": [
                [port_name, slot, participated]
                for (port_name, slot), participated in self._participated.items()
            ],
        }

    def restore_state(self, state: dict[str, Any]) -> None:
        """Restore this sub-timeline's state from a snapshot, for snapshot resume.

        Args:
            state: The saved state, as returned by get_state().
        """
        self._iteration = state["iteration"]
        first_operator = state["first_operator"]
        self._first_operator = (
            Operator[first_operator] if first_operator is not None else None
        )
        self._participated = {
            (port_name, slot): participated
            for port_name, slot, participated in state["participated"]
        }
