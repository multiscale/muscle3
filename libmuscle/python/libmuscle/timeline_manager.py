from typing import Optional

from ymmsl.v0_2 import Operator

from libmuscle.port import Port
from libmuscle.port_manager import PortManager


class TimelineManager:
    """Tracks iteration state for the main timeline and manages sub-timelines.

    O_F and F_INIT ports live in the main timeline tracked by this manager.
    O_I and S ports live in sub-timelines, each managed by a SubTimelineManager.
    Ports with no timeline defined are grouped under the component name.
    """

    def __init__(self, instance_name: str, port_manager: PortManager) -> None:
        """Create a TimelineManager.

        Args:
            instance_name: Component name used as the default timeline key for
                O_I and S ports that have no timeline defined.
            port_manager: The port manager for this instance.
        """
        self._instance_name = instance_name
        self._port_manager = port_manager
        self._iteration: Optional[list[int]] = None

        # Pre-collect F_INIT and O_F ports once; passed as sibling_ports on
        # every O_F send.
        self._sibling_ports: list[Port] = [
            port for port in port_manager._ports.values()
            if port.operator in (Operator.F_INIT, Operator.O_F)
        ]

        self._sub_timelines: dict[str, SubTimelineManager] = {
            key: SubTimelineManager(port_manager, key, instance_name)
            for key in {
                str(port.timeline) if port.timeline else instance_name
                for port in port_manager._ports.values()
                if port.operator in (Operator.O_I, Operator.S)
            }
        }

    def check_send_message(self, port_name: str) -> None:
        """Check and update iteration state before sending on the given port.

        The caller (Instance.__check_port) already guarantees the operator
        allows sending, so the port is either O_F or O_I.

        O_F (needs: self._port_manager, self._iteration, self._sibling_ports):
            1. Not yet started (self._iteration is None):
               self._iteration = []
               port._iteration = self._iteration
               NOTE: Works only for root components (no F_INIT ports). For all other
               components self._iteration is already set by check_receive_message on
               F_INIT before O_F is reached (SEL order: F_INIT → O_I/S loop → O_F). A
               non-root component calling O_F before F_INIT violates SEL order; the MMSF
               validator raises a RuntimeError before this method is reached in that
               case.
            2. Yet started (self._iteration is not None):
                a. Port has not yet sent this iteration (port._iteration is None, or
                   port._iteration[-1] == self._iteration[-1] - 1):
                    port._iteration = self._iteration
                b. Port already sent this iteration (port.iteration = self._iteration):
                    i. Start a new iteration as all siblings have sent/received at
                    self._iteration:
                        self._iteration[-1] += 1
                        port._iteration = self._iteration
                NOTE: O_I and S ports do not need to be checked here. SEL order
                guarantees the sub-timelines are already finished when O_F is reached.
            
            Otherwise → Error.

        O_I (needs: self._iteration, self._port_manager, self._instance_name,
             self._sub_timelines):
            1. If self._iteration is None (root component, first call is O_I):
              - set self._iteration = [].
              NOTE: This can happen for a root component that has no F_INIT ports.
              - call check_send_message of the subtimeline manager of this port:
                    self._sub_timelines[port.timeline].check_send_message()
        """
        pass

    def check_received_message(
            self, port_name: str, iteration: Optional[list[int]]) -> None:
        """Check and update iteration state after receiving on the given port.

        The caller (Instance.__check_port) already guarantees the operator
        allows receiving, so the port is either F_INIT or S.

        F_INIT (needs: self._port_manager, self._iteration, self._sibling_ports):
            1. Not yet started (self._iteration is None):
                self._iteration = list(iteration)
                port._iteration = self._iteration
                NOTE: self._iteration is copied from the sender's iteration, which
                can be a nested list e.g. [1, 2, 3] if the sender is itself nested.
            2. Yet started (self._iteration is not None):
                a. Port has not yet received this iteration (port._iteration is None, or
                   port._iteration[-1] == self._iteration[-1] - 1), and the iteration of
                   the message equals self._iteration:
                    port._iteration = self._iteration
                b. Port already received this iteration
                   (port._iteration == self._iteration) and a new iteration has
                   arrived:
                    i. Check the parent-iteration: Verify 
                    iteration[:-1] >= self._iteration[:-1] (prefix is non-decreasing; 
                    parent iteration never goes backward).
                    ii. Start a new iteration as all siblings have received at
                    self._iteration:
                        self._iteration = list(iteration)
                        port._iteration = self._iteration
                    NOTE: The iteration list can change in value across multiple indices
                    simultaneously, e.g. [0,0]->[0,1]->[0,2]->[1,3]->[1,4]->...,
                    because muscle3 may enter or leave sub-loops between successive
                    F_INIT receives, advancing outer and inner counters at once.

            Otherwise → Error.

        S (needs: self._sub_timelines, self._instance_name):
            - Delegate to check_received_message of the sub-timeline manager for
              this port:
                self._sub_timelines[port.timeline].check_received_message()
            NOTE: self._iteration is always set before an S receive is reached.
            SEL order guarantees that an O_I send (which sets self._iteration for
            root components) or an F_INIT receive (which sets it for non-root
            components) has already occurred before any sub-loop S receive.
        """
        pass

class SubTimelineManager:
    """Tracks iteration state for a single sub-timeline."""

    def __init__(
            self, port_manager: PortManager, sub_timeline: str,
            instance_name: str) -> None:
        """Create a SubTimelineManager.

        Args:
            port_manager: The port manager for this instance.
            sub_timeline: Name of the timeline this manager tracks.
            instance_name: Component name used as the default timeline key for
                ports with no timeline defined; needed to resolve which ports
                belong to this sub-timeline.
        """
        self._sub_timeline = sub_timeline
        self._iteration: Optional[list[int]] = None

        # Pre-collect the O_I and S ports that belong to this sub-timeline once;
        # passed as sibling_ports on every O_I send.
        self._sibling_ports: list[Port] = [
            port for port in port_manager._ports.values()
            if port.operator in (Operator.O_I, Operator.S)
            and (str(port.timeline) if port.timeline else instance_name)
            == sub_timeline
        ]

    def check_send_message(
            self, port: Port, parent_iteration: list[int]) -> None:
        """Check and update iteration state before sending on the given O_I port.

        O_I (needs: port, parent_iteration, self._iteration, self._sibling_ports):
            1. Not yet started (self._iteration is None):
                a. First message send for this instance:
                    self._iteration = parent_iteration + [0]
                    port._iteration = self._iteration
            2. Yet started (self._iteration is not None):
                a. Parent iteration advanced
                   (self._iteration[:-1] != parent_iteration):
                    self._iteration = parent_iteration + [self._iteration[-1]]
                    port._iteration = self._iteration
                    NOTE: The sub-iteration counter keeps running across outer
                    iterations. This must be checked first, before (b) and (c),
                    because the port comparison only makes sense once the prefix
                    is up to date.
                b. Port has not yet sent this iteration (port._iteration is None,
                   or port._iteration[-1] == self._iteration[-1] - 1):
                    port._iteration = self._iteration
                c. Port already sent this iteration (port.iteration = self._iteration):
                    i. Start a new iteration as all siblings have sent/received at
                    self._iteration:
                        self._iteration[-1] += 1
                        port._iteration = self._iteration
                        
            Otherwise → Error.
        """
        pass

    def check_received_message(self, port_name: str, iteration: list[int]) -> None:
        """Check and update iteration state after receiving on the given S port.

        S (needs: port, iteration, self._iteration, self._sibling_ports):
            NOTE: self._iteration is always set before an S receive is reached.
            Within a sub-loop, O_I is always sent before S is received; the first
            O_I send goes through check_send_message which sets self._iteration.
            Case 1 (self._iteration is None) therefore cannot occur here.

            1. Yet started (self._iteration is not None):
                b. Port has not yet received this sub-iteration (port._iteration is 
                None, or port._iteration[-1] == iteration[-1] - 1):
                    self._iteration = list(iteration)
                    port._iteration = self._iteration
                c. Port already received this iteration 
                (port.iteration = self._iteration):
                NOTE: There is no case c. O_I's check_send_message always runs
                before the next S receive (SEL order), so self._iteration is
                already at the new sub-iteration by the time S receives it.
         
            Otherwise → Error.
        """
        pass
