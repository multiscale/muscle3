from typing import Optional

from ymmsl.v0_2 import Operator, Timeline

from libmuscle.port import Port
from libmuscle.port_manager import PortManager


def _port_has_not_yet_participated(port: Port, iteration: list[int]) -> bool:
    """Return True if the port has not yet participated in the current iteration.

    A port has not yet participated when:
    - Has never sent or received: port._iteration is None.
    - Is still at the previous iteration:
        port._iteration[-1] == iteration[-1] - 1).

    Args:
        port: The port to check.
        iteration: The current iteration to check against.

    Returns:
        True if the port has not yet participated in the current iteration.
    """
    pass


def _port_is_at_iteration(port: Port, iteration: list[int]) -> bool:
    """Return True if the port has already participated in the current iteration.

    A port is at the current iteration when: port._iteration[-1] == iteration[-1], 
    meaning it has already sent or received in this iteration.

    Args:
        port: The port to check.
        iteration: The current iteration to check against.

    Returns:
        True if the port has already participated in the current iteration.
    """
    pass


def _all_ports_participated(
        sibling_ports: list[Port], iteration: list[int]) -> bool:
    """Return True if all sibling ports have participated in the current iteration.

    Checks that every port in sibling_ports satisfies _port_is_at_iteration.

    Args:
        sibling_ports: All ports sharing the same timeline.
        iteration: The current iteration to check against.

    Returns:
        True if every sibling port is at the given iteration.
    """
    pass


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
    """

    def __init__(self, instance_name: str, port_manager: PortManager) -> None:
        """Create a TimelineManager.

        Args:
            instance_name: Component name for this instance.
            port_manager: The port manager for this instance.
        """
        self._instance_name = instance_name
        self._port_manager = port_manager
        self._iteration: Optional[list[int]] = None

        # Group all ports by their timeline attribute. 
        #      F_INIT and O_F ports share the same timeline
        #      O_I and S ports belong to sub-timelines.
        self._timelines: dict[Optional[Timeline], list[Port]] = {}
        for port in port_manager._ports.values():
            tl = port.timeline
            if tl not in self._timelines:
                self._timelines[tl] = []
            self._timelines[tl].append(port)

        self._timeline: Optional[Timeline] = next(
            (p.timeline for p in port_manager._ports.values()
             if p.operator in (Operator.F_INIT, Operator.O_F)),
            None
        )

        self._sub_timelines: dict[Optional[Timeline], SubTimelineManager] = {
            tl: SubTimelineManager(tl, ports)
            for tl, ports in self._timelines.items()
            if tl != self._timeline
        }

    def check_send_message(self, port_name: str) -> None:
        """Check and update iteration state before sending on the given port.

        NOTE: The caller (Instance.__check_port) already guarantees the operator
        allows sending, so the port is either O_F or O_I.

        O_F:
            1. Not yet started (self._iteration is None):
                   self._iteration = []
                   port._iteration = self._iteration
                   NOTE: Works only for root components (no F_INIT ports). For
                   all other components self._iteration is already set by
                   check_received_message on F_INIT before O_F is reached (SEL
                   order: F_INIT → O_I/S loop → O_F). A non-root component
                   calling O_F before F_INIT violates SEL order; the MMSF
                   validator raises a RuntimeError before this method is reached.

            2. Yet started (self._iteration is not None):
                a. _port_has_not_yet_participated(port, self._iteration):
                b. _port_is_at_iteration(port, self._iteration):
                   i. _all_ports_participated(self._timelines[self._timeline],
                      self._iteration):
                          _advance_iteration(self._iteration)
                      NOTE: SEL order guarantees the sub-timelines are already
                      finished when O_F is reached.
                port._iteration = self._iteration

            Otherwise → Error.

        O_I:
            1. Not yet started (self._iteration is None): 
                   self._iteration = []
                NOTE: This can happen for a root component that has no F_INIT ports.
            self._sub_timelines[port.timeline].check_send_message(port, self._iteration)
        """
        pass

    def check_received_message(
            self, port_name: str, iteration: Optional[list[int]]) -> None:
        """Check and update iteration state after receiving on the given port.

        NOTE: The caller (Instance.__check_port) already guarantees the operator
        allows receiving, so the port is either F_INIT or S.

        F_INIT:
            1. Not yet started (self._iteration is None):
                self._iteration = iteration
                NOTE: self._iteration is copied from the sender's iteration, which can
                be a nested list e.g. [1, 2, 3] if the sender is itself nested.
            2. Yet started (self._iteration is not None):
                a. _port_has_not_yet_participated(port, self._iteration) and
                   iteration == self._iteration (correct message)
                b. _port_is_at_iteration(port, self._iteration) and a new
                   iteration has arrived (iteration != self._iteration):
                       self._iteration = iteration
                       NOTE: The iteration list can change across multiple
                       indices simultaneously, e.g. [0,0]→[0,1]→[1,3]→...,
                       because muscle3 may enter or leave sub-loops between
                       successive F_INIT receives, advancing outer and inner
                       counters at once.
            port._iteration = self._iteration

            Otherwise → Error.

        S: self._sub_timelines[port.timeline].check_received_message(port, iteration).
        NOTE: self._iteration is always set before an S receive is reached. SEL order
        guarantees that an O_I send or an F_INIT receive has already occurred before any
        sub-loop S receive.
        """
        pass

class SubTimelineManager:
    """Tracks iteration state for a single sub-timeline."""

    def __init__(
            self, sub_timeline: Optional[Timeline],
            sibling_ports: list[Port]) -> None:
        """Create a SubTimelineManager.

        Args:
            sub_timeline: The timeline this manager tracks.
            sibling_ports: All O_I and S ports belonging to this sub-timeline,
                pre-selected from TimelineManager._timelines.
        """
        self._sub_timeline = sub_timeline
        self._iteration: Optional[list[int]] = None
        self._sibling_ports = sibling_ports

    def check_send_message(
            self, port: Port, parent_iteration: list[int]) -> None:
        """Check and update iteration state before sending on the given O_I port.

            1. Not yet started (self._iteration is None):
                   self._iteration = parent_iteration + [0]
            2. Yet started (self._iteration is not None):
                a. Check if parent iteration advanced: 
                   self._iteration[:-1] != parent_iteration
                   self._iteration = parent_iteration + [self._iteration[-1]]
                NOTE: The sub-iteration counter keeps running across outer iterations.
                This must be checked first.
                    i. _port_has_not_yet_participated(port, self._iteration):
                    ii. _port_is_at_iteration(port, self._iteration):
                        _all_ports_participated(self._sibling_ports, self._iteration):
                            _advance_iteration(self._iteration)
            port._iteration = self._iteration

            Otherwise → Error.
        """
        pass

    def check_received_message(self, port_name: str, iteration: list[int]) -> None:
        """Check and update iteration state after receiving on the given S port.

        NOTE: self._iteration is always set before an S receive is reached.
        Within a sub-loop, O_I is always sent before S is received.

        1. _port_has_not_yet_participated(port, iteration):
                self._iteration = iteration
                port._iteration = self._iteration
        NOTE: O_I's check_send_message always runs before the next S receive (SEL order)
        so self._iteration is already at the new sub-iteration by the time S receives it

        Otherwise → Error.
        """
        pass
