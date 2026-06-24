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
