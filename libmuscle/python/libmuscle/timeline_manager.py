from typing import Optional

from ymmsl.v0_2 import Operator

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
        self._iteration: Optional[list[int]] = None

        self._sub_timelines: dict[str, SubTimelineManager] = {
            key: SubTimelineManager(port_manager, key)
            for key in {
                str(port.timeline) if port.timeline else instance_name
                for port in port_manager._ports.values()
                if port.operator in (Operator.O_I, Operator.S)
            }
        }


class SubTimelineManager:
    """Tracks iteration state for this timeline."""

    def __init__(self, port_manager: PortManager, sub_timeline: str) -> None:
        """Create a SubTimelineManager.

        Args:
            port_manager: The port manager for this instance.
            sub_timeline: Name of the timeline this manager tracks.
        """
        self._iteration: Optional[list[int]] = None
