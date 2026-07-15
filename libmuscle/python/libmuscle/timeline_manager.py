from typing import Optional

from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager


def _all_ports_participated(
    ports: list[Port],
    participated: dict[str, bool],
    operator: Optional[Operator] = None,
) -> bool:
    """Return True if every matching port has participated in the current iteration.

    Args:
        ports: All ports sharing the same (sub)timeline.
        participated: Whether each port, keyed by name, has sent or received a
            message for the current iteration.
        operator: If given, only ports with this operator are considered;
            otherwise every port in ports is considered.

    Returns:
        True if every matching port has participated.
    """
    return all(
        participated[str(port.name)]
        for port in ports
        if operator is None or port.operator == operator
    )


def _reset_participation(participated: dict[str, bool]) -> None:
    """Mark every port as not yet participated, for a new iteration.

    Must be called whenever _advance_iteration is called, since starting a
    new iteration means none of the ports have participated in it yet.

    Args:
        participated: Whether each port, keyed by name, has sent or received a
            message for the current iteration. Modified in-place, reset to
            all False.
    """
    for port_name in participated:
        participated[port_name] = False


def _advance_iteration(iteration: list[int]) -> None:
    """Increment the sub-iteration counter in-place.

    Advances the last element of iteration by one.

    Args:
        iteration: The current iteration state. Modified in-place.
    """
    iteration[-1] += 1


class TimelineManager:
    """Tracks iteration state for the main timeline and manages sub-timelines.

    O_F and F_INIT ports live in the main timeline tracked by this manager.
    O_I and S ports live in sub-timelines, each managed by a SubTimelineManager.
    All ports are grouped by their timeline attribute in _timelines.

    The TimelineManager (and each SubTimelineManager) keeps a dict of booleans in
    self._participated, keyed by port name, recording whether each port has already
    sent or received a message for the current iteration.

    BRIDGE: A component exchanging data through O_I/S ports between two or more
    timelines. Normally all O_I ports must send before any S port may receive; for a
    bridge, that ordering is not required, either operator may go first on a given
    sub-timeline, and sends/receives may interleave in any order. Completeness is not
    relaxed: every O_I and S port on a leg must still participate before the iteration
    advances. See SubTimelineManager for where this is implemented.

    TODO (bridge): Require knowledge whether this instance/timeline is a bridge, and
    pass this on to the SubTimelineManagers.

    TODO: Add a skip_checks, the instance-wide InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS
    (for cases like ImplementationTester).
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
        self._participated: dict[str, bool] = {}
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
        ]
        self._participated = {str(port.name): False for port in self._ports}

        sub_timelines = {
            self._port_manager.get_port(name).timeline
            for op in (Operator.O_I, Operator.S)
            for name in all_ports.get(op, [])
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

    def check_send_message(self, port_name: str) -> None:
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
        is_root = not any(
            p.is_connected() for p in self._ports if p.operator == Operator.F_INIT
        )

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
                self._participated[port_name] = True
                if _all_ports_participated(self._ports, self._participated):
                    self.reset()
                return

            if not _all_ports_participated(
                self._ports, self._participated, Operator.F_INIT
            ):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but not all'
                    " F_INIT ports have received a message for this iteration yet."
                )

            if self._participated[port_name]:
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

            self._participated[port_name] = True
            if _all_ports_participated(self._ports, self._participated):
                self.reset()
            return

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

            self._sub_timelines[port.timeline].check_send_message(port, self._iteration)
            return

        raise RuntimeError(
            f'Port "{port_name}" is not an O_F or O_I port, and cannot send a'
            " message here."
        )

    def check_receive(self, port_name: str) -> None:
        """Check that receiving on the given port is currently allowed.

        NOTE: The caller (Instance.__check_port) already guarantees the operator
        allows receiving, so the port is either F_INIT or S.

        F_INIT:
            1. Not yet started (self._iteration is None): Allowed.
            2. Yet started (self._iteration is not None):
                   not self._participated[port_name]: Allowed.
            NOTE: Only reachable with multiple F_INIT ports. The first port always hits
            case 1 (self._iteration is None after reset). Subsequent ports in the same
            cycle arrive here with the same iteration. A new iteration never arrives
            here, after reset() self._iteration is None, so any new iteration lands in
            case 1.

            Otherwise --> error.

        S:
            1. self._iteration is None, the sub-timeline is a bridge, and this
               is a root component (no connected F_INIT ports): Allowed.
            2. self._iteration is not None (O_I was sent, F_INIT was received,
               or case 1a just allowed it):
                   self._sub_timelines[port.timeline].check_receive(
                       port, self._iteration)
        """
        pass

    def check_received_message(
        self, port_name: str, iteration: Optional[list[int]]
    ) -> None:
        """Record that a message has been received on the given port.

        NOTE: check_receive already established that this receive is legal; this
        only records that the port has participated, which is only known once
        the message has actually arrived.

        F_INIT:
            1. Not yet started (self._iteration is None):
                self._iteration = iteration
                NOTE: self._iteration is copied from the sender's iteration, which can
                be a nested list e.g. [1, 2, 3] if the sender is itself nested.
            2. Yet started (self._iteration is not None)
                iteration == self._iteration, otherwise → Error (wrong message;
                check_receive only confirmed this port was allowed to receive, not
                which iteration the message would carry).
            self._participated[port_name] = True

        S:
            1. self._iteration is None (check_receive case S.1a already confirmed
               the sub-timeline is a bridge and this is a root component):
                   self._iteration = []
            2. self._iteration is not None (O_I was sent, F_INIT was received,
               or case 1 just fired):
                   self._sub_timelines[port.timeline].check_received_message(
                       port, iteration)
        """
        pass

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

        self._ports = [
            port_manager.get_port(name)
            for op in (Operator.O_I, Operator.S)
            for name in port_manager.list_ports(sub_timeline).get(op, [])
        ]
        self._participated = {str(port.name): False for port in self._ports}

    def check_send_message(self, port: Port, parent_iteration: list[int]) -> None:
        """Check and update this sub-timeline's iteration state before sending.

        The first message sent on any O_I port of this sub-timeline starts its iteration
        nested one level below the main timeline's current iteration. Afterwards, an O_I
        port that has already sent for the current sub-iteration may send again only
        once every O_I and S port of this sub-timeline has participated, in which case
        the sub-iteration advances and participation is reset for the new one.

        Args:
            port: The O_I port that is about to send.
            parent_iteration: The main timeline's current iteration, used to
                start this sub-timeline's iteration the first time a message
                is sent on it.

        Raises:
            RuntimeError: If this port already sent a message for the
                current sub-iteration and not every port of this
                sub-timeline has participated yet, so the sub-iteration
                cannot advance.
        """
        port_name = str(port.name)

        if self._iteration is None:
            self._iteration = parent_iteration + [0]
        elif self._participated[port_name]:
            if not _all_ports_participated(self._ports, self._participated):
                raise RuntimeError(
                    f'Port "{port_name}" tried to send a message, but it already'
                    " sent one for this sub-iteration and not every port of this"
                    " sub-timeline has participated yet."
                )
            _advance_iteration(self._iteration)
            _reset_participation(self._participated)

        self._participated[port_name] = True

    def get_iteration(self) -> Optional[list[int]]:
        """Return the current iteration of this sub-timeline."""
        return self._iteration

    def check_receive(self, port: Port, parent_iteration: list[int]) -> None:
        """Check that receiving on the given S port is currently allowed.

        1. Not yet started (self._iteration is None):
               a. sub_timeline is a bridge:
                      Allowed.
               b. Otherwise → Error (no O_I port has sent yet on this
                  sub-timeline).
        2. Yet started (self._iteration is not None):
               a. not self._participated[str(port.name)]:
                      Allowed, unless the sub-timeline is not a bridge and
                      not _all_ports_participated(
                          self._ports, self._participated, Operator.O_I)
                      → Error (not every O_I port has sent yet).
               b. self._participated[str(port.name)]:
                      Allowed only if the sub-timeline is a bridge (bridges
                      permit interleaved sends/receives within the same
                      iteration).

               Otherwise → Error.
        """
        pass

    def check_received_message(self, port_name: str, iteration: list[int]) -> None:
        """Record that a message has been received on the given S port.

        1. self._iteration is None (check_receive case 1a already confirmed
           the sub-timeline is a bridge):
               self._iteration = iteration
               self._participated[port_name] = True
        2. self._iteration is not None:
            a. not self._participated[port_name]
               (check_receive case 2a already confirmed this is allowed):
                    self._iteration = iteration
                    self._participated[port_name] = True
            b. self._participated[port_name]
               (check_receive case 2b already confirmed the sub-timeline is a
               bridge):
                 _all_ports_participated(self._ports, self._participated):
                       _advance_iteration(self._iteration)
                       _reset_participation(self._participated)
                 self._participated[port_name] = True
        """
        pass

    def reset(self) -> None:
        """Reset this sub-timeline once the main timeline's cycle completes.

        Called by TimelineManager.reset(). Clears this sub-timeline's iteration and
        participation state, so that the next message sent on one of its O_I ports
        starts a new sub-timeline iteration.
        """
        self._iteration = None
        _reset_participation(self._participated)
