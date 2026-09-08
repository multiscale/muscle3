from dataclasses import asdict, dataclass

from libmuscle.mpp_message import MPPMessage
from libmuscle.timeline_manager import PortAndSlot, TimelineState


@dataclass
class CommunicatorState:
    port_message_counts: dict[str, list[int]]
    timeline_state: TimelineState
    message_cache: dict[PortAndSlot, MPPMessage]

    def asdict(self) -> dict:
        """Convert CommunicatorState into a MsgPack-serializable dictionary."""
        return {
            "port_message_counts": self.port_message_counts,
            "timeline_state": asdict(self.timeline_state),
            "message_cache": [
                [port_name, slot, msg.encoded()]
                for (port_name, slot), msg in self.message_cache.items()
            ],
        }

    @classmethod
    def fromdict(cls, data: dict) -> "CommunicatorState":
        """Create CommunicatorState from a MsgPack-serializable dictionary."""
        return cls(
            data["port_message_counts"],
            TimelineState(**data["timeline_state"]),
            {
                (port_name, slot): MPPMessage.from_bytes(encoded)
                for port_name, slot, encoded in data["message_cache"]
            },
        )
