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

    Advances the last element of iteration by one, signalling that all sibling
    ports have participated in the current iteration and a new one is beginning.

    Args:
        iteration: The current iteration state. Modified in-place.
    """
    pass


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
        """Check and update iteration state before sending on the given port.

        NOTE: The caller (Instance.__check_port) already guarantees the operator
        allows sending, so the port is either O_F or O_I.

        O_F:
            1. Not yet started (self._iteration is None):
                a. Root component (no connected F_INIT ports):
                       self._iteration = []
                       If self._sub_timelines: → Error.
                       self._participated[port_name] = True
                       if _all_ports_participated(self._ports, self._participated):
                           self.reset()
                b. Otherwise → Error.

            2. Yet started (self._iteration is not None):
                Check _all_ports_participated(
                    self._ports, self._participated, Operator.F_INIT),
                otherwise → Error.
                a. not self._participated[port_name]:
                       for stm in self._sub_timelines.values():
                           if stm._iteration is not None:
                               _all_ports_participated(
                                   stm._ports, stm._participated)
                           Otherwise → Error.
                       self._participated[port_name] = True
                       if _all_ports_participated(self._ports, self._participated):
                           self.reset()
                b. self._participated[port_name]: → Error

            Otherwise → Error.

        O_I:
            1. Not yet started (self._iteration is None):
                a. Is it a root component? If it has no connected F_INIT ports:
                       self._iteration = []
                b. Otherwise → Error.
            2. Yet started (self._iteration is not None):
                Check _all_ports_participated(
                    self._ports, self._participated, Operator.F_INIT),
                otherwise → Error.

            self._sub_timelines[port.timeline].check_send_message(port, self._iteration)
        """
        pass

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
        """Reset iteration state after all O_F ports have sent.

        Called from check_send_message O_F case 2b.i, if all sibling O_F
        ports have participated: Resets self._iteration to None, resets
        self._participated to all False (via _reset_participation) for every
        F_INIT and O_F port on the main timeline, and calls reset() on
        every SubTimelineManager so their sub-iteration counters and
        participation are also reset.

        After this call the next F_INIT receive re-initialises self._iteration
        via case 1.
        """
        pass


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
        """Check and update iteration state before sending on the given O_I port.

        1. Not yet started (self._iteration is None):
               self._iteration = parent_iteration + [0]
        2. Yet started (self._iteration is not None):
            a. not self._participated[str(port.name)]:
                   Allowed.
            b. self._participated[str(port.name)]:
                   _all_ports_participated(self._ports, self._participated):
                           _advance_iteration(self._iteration)
                           _reset_participation(self._participated)
                   Otherwise → Error.

        self._participated[str(port.name)] = True

        Otherwise → Error.
        """
        pass

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
        """Reset iteration state when the sub-timeline's cycle is complete.

        Called by TimelineManager.reset(). Resets self._iteration to None and
        resets self._participated to all False (via _reset_participation) for
        every O_I and S port in this sub-timeline.
        """
        pass
