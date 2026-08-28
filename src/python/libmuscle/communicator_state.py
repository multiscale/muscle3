from dataclasses import asdict, dataclass

from libmuscle.timeline_manager import TimelineState


@dataclass
class CommunicatorState:
    port_message_counts: dict[str, list[int]]
    timeline_state: TimelineState
    # TODO: message cache

    def asdict(self) -> dict:
        """Convert CommunicatorState into a MsgPack-serializable dictionary."""
        return {
            "port_message_counts": self.port_message_counts,
            "timeline_state": asdict(self.timeline_state),
        }

    @classmethod
    def fromdict(cls, data: dict) -> "CommunicatorState":
        """Create CommunicatorState from a MsgPack-serializable dictionary."""
        return cls(
            data["port_message_counts"],
            TimelineState(**data["timeline_state"]),
        )
