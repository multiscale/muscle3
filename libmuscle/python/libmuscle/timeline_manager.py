from typing import Optional

from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager

_ParticipationKey = tuple[str, Optional[int]]


def _slots(port: Port) -> list[Optional[int]]:
    """Return the slots to track participation for on the given port.

    A vector port has one slot per element (each of which may be sent or
    received on independently, e.g. because it connects to a different peer
    instance); a scalar port has a single, slot-less, entry.

    Args:
        port: The port to get the slots of.

    Returns:
        A list of slots, or [None] for a scalar port.
    """
    if port.is_vector():
        return list(range(port.get_length()))
    return [None]


def _all_ports_participated(
    ports: list[Port],
    participated: dict[_ParticipationKey, bool],
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


def _any_port_participated(
    ports: list[Port],
    participated: dict[_ParticipationKey, bool],
    operator: Optional[Operator] = None,
) -> bool:
    """Return True if any matching port (or slot of it) has participated.

    Args:
        ports: All ports sharing the same (sub)timeline.
        participated: Whether each port and slot, keyed by (name, slot), has
            sent or received a message for the current iteration.
        operator: If given, only ports with this operator are considered;
            otherwise every port in ports is considered.

    Returns:
        True if any matching port (or slot of it) has participated.
    """
    return any(
        participated.get((str(port.name), slot), False)
        for port in ports
        if operator is None or port.operator == operator
        for slot in _slots(port)
    )


def _reset_participation(participated: dict[_ParticipationKey, bool]) -> None:
    """Mark every port and slot as not yet participated, for a new iteration.

    Must be called whenever _advance_iteration is called, since starting a
    new iteration means none of the ports have participated in it yet.

    Args:
        participated: Whether each port and slot, keyed by (name, slot), has
            sent or received a message for the current iteration. Modified
            in-place, reset to all False.
    """
    for key in participated:
        participated[key] = False


def _advance_iteration(iteration: list[int]) -> None:
    """Increment the sub-iteration counter in-place.

    Advances the last element of iteration by one.

    Args:
        iteration: The current iteration state. Modified in-place.
    """
    iteration[-1] += 1


class TimelineManager:
    """Tracks iteration state for the main timeline and manages sub-timelines.

    O_F and F_INIT ports live on the main timeline, tracked directly by this
    manager. O_I and S ports live on sub-timelines, each tracked by its own
    SubTimelineManager, grouped by the port's timeline attribute.

    Every TimelineManager and SubTimelineManager records, for each of its
    ports, whether that port has already sent or received a message for the
    current iteration, in a dict of booleans keyed by port name.

    TODO: Support an instance-wide skip_checks flag
    (InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS), for cases such as
    ImplementationTester.
    """

    def __init__(self, instance_name: str, port_manager: PortManager) -> None:
        """Create a TimelineManager.

        This only stores the instance name and port manager. The sub-timelines
        cannot be determined yet, since port.timeline is only populated once
        the ports have been connected to their peers.

        Args:
            instance_name: Component name for this instance.
            port_manager: The port manager for this instance.
        """
        self._instance_name = instance_name
        self._port_manager = port_manager
        self._iteration: Optional[list[int]] = None
        self._ports: list[Port] = []
        self._participated: dict[_ParticipationKey, bool] = {}
        self._sub_timelines: dict[Timeline, SubTimelineManager] = {}

    def connect_sub_timelines(self) -> None:
        """Create the SubTimelineManagers once the ports are connected.

        This must be called after PortManager.connect_ports() has run, since
        it reads port.timeline from the connected ports. Also collects the
        main-timeline (F_INIT and O_F) ports and their participation tracking.
        """
        all_ports = self._port_manager.list_ports()

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

        # NOTE: The timeline strings received from the manager are the local relative
        # names declared in yMMSL (e.g. "tl1"), not full absolute paths. For nested
        # topologies (e.g. a micro component under meso and macro) the correct
        # absolute timeline would be ":macro:meso", but only the local name is sent.
        # Assumes every O_I/S port has a non-empty timeline.
        self._sub_timelines = {
            tl: SubTimelineManager(tl, self._port_manager) for tl in sub_timelines
        }

    def get_iteration(self, port_name: str) -> Optional[list[int]]:
        """Return the iteration to embed in an outgoing message on the given port.

        Args:
            port_name: The name of an O_F or O_I port that is about to send.

        Returns:
            self._iteration for an O_F port, or the iteration of the
            sub-timeline the port lives on for an O_I port.
        """
        port = self._port_manager.get_port(port_name)
        if port.operator == Operator.O_F:
            return self._iteration
        return self._sub_timelines[port.timeline].get_iteration()

    def _is_root(self) -> bool:
        """Return whether this component has no connected F_INIT ports.

        A root component may still declare F_INIT ports, as long as none of
        them are connected to a peer; a component that declares no F_INIT
        ports at all is trivially root.
        """
        return not any(
            p.is_connected() for p in self._ports if p.operator == Operator.F_INIT
        )

    def check_send_message(
        self, port_name: str, slot: Optional[int] = None
    ) -> list[int]:
        """Check and update the timeline state before sending on the given port.

        A component is root if it has no connected F_INIT ports, and on a root component
        the first message sent on an O_F or O_I port starts the main timeline at
        iteration []. Any other component must first receive a message on every F_INIT
        port before it may send on O_F or O_I. The iteration it starts on is then simply
        copied from that message (see check_received_message).

        Once the timeline has started, an O_F port may send again only once every F_INIT
        port has received a message for the current iteration and every sub-timeline
        that has started has completed its current iteration. Once the last O_F port has
        sent for the current iteration, the main timeline is reset in preparation for
        the next one, which also resets every sub-timeline.

        An O_I port only starts or validates the main timeline as described above. The
        corresponding sub-timeline's iteration is advanced separately, by delegating to
        SubTimelineManager.check_send_message.

        Args:
            port_name: Name of the O_F or O_I port that is about to send. The
                caller (Instance.__check_port) has already confirmed that
                this operator is allowed to send.
            slot: The slot being sent on, if this is a vector port.

        Returns:
            The iteration to embed in the outgoing message. Captured before
            any reset triggered by this same send, so that a send which
            completes the current (sub-)iteration still embeds the iteration
            it belongs to, rather than the one that follows it.

        Raises:
            RuntimeError: If sending on this port at this point would
                violate the Multiscale Modeling and Simulation Framework,
                e.g. because F_INIT has not been received yet on a non-root
                component, this port already sent a message for the current
                iteration, not every F_INIT port has received yet, an
                unfinished sub-timeline remains, or a root component
                declares O_I/S ports (a root component cannot have
                sub-timelines).
        """
        port = self._port_manager.get_port(port_name)
        is_root = self._is_root()

        if port.operator == Operator.O_F:
            if self._iteration is None:
                if not is_root:
                    raise RuntimeError(
                        f'Port "{port_name}" tried to send the first message on the'
                        " main timeline, but this component has connected F_INIT"
                        " ports and must receive on all of them first."
                    )
                if self._sub_timelines:
                    raise RuntimeError(
                        f'Port "{port_name}" tried to send the first message on the'
                        " main timeline, but this component has sub-timelines. A"
                        " root component may not have O_I or S ports."
                    )
                self._iteration = []
                self._participated[(port_name, slot)] = True
                iteration = self._iteration
                if _all_ports_participated(self._ports, self._participated):
                    self.reset()
                return iteration

            if not _all_ports_participated(
                self._ports, self._participated, Operator.F_INIT
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            if self._participated.get((port_name, slot), False):
                raise RuntimeError(
                    f'Port "{port_name}" already sent a message for this iteration.'
                )

            for stm in self._sub_timelines.values():
                if stm._iteration is not None and not _all_ports_participated(
                    stm._ports, stm._participated
                ):
                    raise RuntimeError(
                        f'Port "{port_name}" tried to send a message, but a'
                        " sub-timeline has not yet completed its current iteration."
                    )

            self._participated[(port_name, slot)] = True
            iteration = self._iteration
            if _all_ports_participated(self._ports, self._participated):
                self.reset()
            return iteration

        if port.operator == Operator.O_I:
            if self._iteration is None:
                if not is_root:
                    raise RuntimeError(
                        f'Port "{port_name}" tried to send the first message, but'
                        " this component has connected F_INIT ports and must"
                        " receive on all of them first."
                    )
                self._iteration = []
            elif not _all_ports_participated(
                self._ports, self._participated, Operator.F_INIT
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            return self._sub_timelines[port.timeline].check_send_message(
                port, slot, self._iteration
            )

        raise RuntimeError(
            f'Port "{port_name}" is not an O_F or O_I port, and cannot send a'
            " message here."
        )

    def check_receive(self, port_name: str, slot: Optional[int] = None) -> None:
        """Check that receiving on the given port is currently allowed.

        An F_INIT port may always receive before the main timeline has
        started, and afterwards may receive again as long as it has not
        already received a message for the current iteration; this only
        matters when there are multiple F_INIT ports, since the first one to
        receive in a cycle always finds the main timeline not yet started.

        An S port is gated the same way an O_I port is gated for sending: on
        a root component, S may receive before the main timeline has
        started; any other component must first receive a message on every
        F_INIT port. Once that is satisfied, whether this specific S port
        may receive is delegated to the corresponding SubTimelineManager.

        Args:
            port_name: Name of the F_INIT or S port about to receive. The
                caller (Instance.__check_port) has already confirmed that
                this operator is allowed to receive.
            slot: The slot being received on, if this is a vector port.

        Raises:
            RuntimeError: If this F_INIT port already received a message for
                the current iteration, if this S port's component is
                non-root and has not yet received on every F_INIT port, or
                if receiving on this S port would violate its sub-timeline's
                ordering or completeness (see SubTimelineManager.check_receive).
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
                if not self._is_root():
                    raise RuntimeError(
                        f'Port "{port_name}" tried to receive the first message,'
                        " but this component has connected F_INIT ports and must"
                        " receive on all of them first."
                    )
            elif not _all_ports_participated(
                self._ports, self._participated, Operator.F_INIT
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to receive a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            self._sub_timelines[port.timeline].check_receive(port, slot)
            return

        raise RuntimeError(
            f'Port "{port_name}" is not an F_INIT or S port, and cannot'
            " receive a message here."
        )

    def check_received_message(
        self,
        port_name: str,
        iteration: Optional[list[int]],
        slot: Optional[int] = None,
    ) -> None:
        """Record that a message has been received on the given port.

        check_receive already established that this receive is legal.

        For an F_INIT port, if the main timeline has not started yet, its
        iteration is adopted from the message (which may be a nested list,
        if the sender is itself on a nested sub-timeline); otherwise the
        message must carry the same iteration the main timeline is already
        on.

        For an S port, if the main timeline has not started yet (only
        possible on a root component receiving before any O_I has sent), it
        starts at iteration []; recording the message itself is then
        delegated to the corresponding SubTimelineManager.

        Args:
            port_name: Name of the F_INIT or S port a message was received
                on.
            iteration: The iteration the received message was sent with.
            slot: The slot the message was received on, if this is a vector
                port.

        Raises:
            RuntimeError: If an already-started F_INIT port received a
                message with an iteration different from the one the main
                timeline is on, or if a message without an iteration was
                received on an S port.
        """
        port = self._port_manager.get_port(port_name)

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

        if port.operator == Operator.S:
            if iteration is None:
                raise RuntimeError(
                    f'Port "{port_name}" received a message without an iteration.'
                )
            if self._iteration is None:
                self._iteration = []
            self._sub_timelines[port.timeline].check_received_message(
                port_name, slot, iteration
            )
            return

        raise RuntimeError(
            f'Port "{port_name}" is not an F_INIT or S port, and cannot'
            " receive a message here."
        )

    def reset(self) -> None:
        """Reset the main timeline once every O_F port has sent for this iteration.

        Called from check_send_message, once every O_F port on the main timeline has
        sent a message for the current iteration. Clears the main timeline's iteration
        and participation state, and resets every sub-timeline in turn, so that the next
        message received on F_INIT starts a new main timeline iteration.
        """
        self._iteration = None
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
        starts its iteration, nested one level below the main timeline's current
        iteration, and establishes O_I as the operator that leads this sub-timeline:
        from then on, every sub-iteration follows the order O_I-then-S, and it is a
        send on O_I, once every O_I and S port (and slot) of this sub-timeline has
        participated, that advances to the next sub-iteration. If S led instead
        (received before any O_I port had sent), an O_I port may still send its one
        message per sub-iteration, but only a receive on S can advance to the next
        one; a second send on the same O_I port and slot before that happens is
        rejected.

        Args:
            port: The O_I port that is about to send.
            slot: The slot being sent on, if this is a vector port.
            parent_iteration: The main timeline's current iteration, used to
                start this sub-timeline's iteration the first time a message
                is sent on it.

        Returns:
            The sub-timeline iteration to embed in the outgoing message.
            Captured after advancing (if this send starts a new
            sub-iteration), so it always reflects the sub-iteration this
            message actually belongs to.

        Raises:
            RuntimeError: If this port and slot already sent a message for the
                current sub-iteration and either S led this sub-timeline (only a
                receive on S may advance it) or not every port of this
                sub-timeline has participated yet.
        """
        port_name = str(port.name)
        key = (port_name, slot)

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
            self._first_operator = Operator.O_I
        elif self._participated.get(key, False):
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
            _advance_iteration(self._iteration)
            _reset_participation(self._participated)

        self._participated[key] = True
        return list(self._iteration)

    def get_iteration(self) -> Optional[list[int]]:
        """Return the current iteration of this sub-timeline."""
        return self._iteration

    def check_receive(self, port: Port, slot: Optional[int] = None) -> None:
        """Check that receiving on the given S port is currently allowed.

        If this S port has not yet received for the current sub-iteration,
        it may do so as long as either no O_I port of this sub-timeline has
        sent yet (this S port would be the first to act, establishing S as
        the operator that leads this sub-timeline) or every O_I port has
        already sent. If this S port already received for the current
        sub-iteration, it may receive again, advancing to the next
        sub-iteration, only if S led this sub-timeline and every S port has
        received; if O_I led instead, only a send on O_I can advance it, and
        a second receive on S before that happens is rejected.

        No pre-declared bridge role is needed for this: whichever operator,
        O_I or S, acts first for a sub-iteration determines that
        sub-iteration's order, and either order is accepted as long as
        completeness is respected.

        Args:
            port: The S port that is about to receive.
            slot: The slot being received on, if this is a vector port.

        Raises:
            RuntimeError: If this S port has not yet received for the
                current sub-iteration and only some, not all, of this
                sub-timeline's O_I ports have sent so far, or if it already
                received for the current sub-iteration and either O_I led
                this sub-timeline (only a send on O_I may advance it) or not
                every S port has received yet.
        """
        port_name = str(port.name)

        if not self._participated.get((port_name, slot), False):
            any_o_i_participated = _any_port_participated(
                self._ports, self._participated, Operator.O_I
            )
            if any_o_i_participated and not _all_ports_participated(
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

        if not _all_ports_participated(self._ports, self._participated, Operator.S):
            raise RuntimeError(
                f'Port "{port_name}" already received a message for this'
                " sub-iteration, and not every S port of this sub-timeline"
                " has received yet."
            )

    def check_received_message(
        self, port_name: str, slot: Optional[int], iteration: list[int]
    ) -> None:
        """Record that a message has been received on the given S port.

        check_receive already established that this receive is legal.

        If this sub-timeline has not started yet, its iteration is adopted
        from the message and S is recorded as the operator that leads this
        sub-timeline: this only happens when this S port is the first to act
        for this sub-timeline, ahead of any O_I port. If this port and slot
        has not yet received for the current sub-iteration, the message must
        carry that same iteration. If this port and slot already received for
        the current sub-iteration, check_receive has already confirmed every
        port of this sub-timeline has participated, so the sub-iteration
        advances and participation is reset for the new one.

        Args:
            port_name: Name of the S port a message was received on.
            slot: The slot the message was received on, if this is a vector
                port.
            iteration: The iteration the received message was sent with.

        Raises:
            RuntimeError: If this port and slot has not yet received for the
                current sub-iteration and the message's iteration does not
                match this sub-timeline's current iteration.
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
            _advance_iteration(self._iteration)
            _reset_participation(self._participated)

        self._participated[key] = True

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's cycle completes.

        Called by TimelineManager.reset(). Clears this sub-timeline's iteration,
        participation state, and leading operator, so that the next message sent or
        received on one of its O_I or S ports starts a new sub-timeline iteration and
        freely re-establishes which operator leads it.
        """
        self._iteration = None
        self._first_operator = None
        _reset_participation(self._participated)
