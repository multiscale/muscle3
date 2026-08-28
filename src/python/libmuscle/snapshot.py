from dataclasses import dataclass
from typing import ClassVar, Optional, cast

import msgpack
from typing_extensions import Buffer
from ymmsl.v0_2 import Reference, Settings

from libmuscle import communicator
from libmuscle.communicator_state import CommunicatorState
from libmuscle.mpp_message import MPPMessage


@dataclass
class Snapshot:
    """Snapshot data structure."""

    SNAPSHOT_VERSION_BYTE: ClassVar[bytes] = b"2"

    triggers: list[str]
    wallclock_time: float
    is_final_snapshot: bool
    message: Optional["communicator.Message"]
    settings_overlay: Settings
    communicator_state: CommunicatorState

    @classmethod
    def from_bytes(cls, data: bytes) -> "Snapshot":
        dct = msgpack.loads(data)
        return cls(
            dct["triggers"],
            dct["wallclock_time"],
            dct["is_final_snapshot"],
            cls.bytes_to_message(dct["message"]),
            Settings(dct["settings_overlay"]),
            CommunicatorState.fromdict(dct["communicator_state"]),
        )

    def to_bytes(self) -> bytes:
        return cast(
            bytes,
            msgpack.dumps(
                {
                    "triggers": self.triggers,
                    "wallclock_time": self.wallclock_time,
                    "is_final_snapshot": self.is_final_snapshot,
                    "message": self.message_to_bytes(self.message),
                    "settings_overlay": self.settings_overlay.as_ordered_dict(),
                    "communicator_state": self.communicator_state.asdict(),
                }
            ),
        )

    @staticmethod
    def message_to_bytes(message: Optional["communicator.Message"]) -> Buffer:
        """Use MPPMessage serializer for serializing the message object"""
        if message is None:
            return b""
        settings = Settings()
        if message.settings is not None:
            settings = message.settings
        return MPPMessage(
            Reference("_"),
            Reference("_"),
            None,
            message.timestamp,
            message.next_timestamp,
            settings,
            0,
            message.data,
            [],
        ).encoded()

    @staticmethod
    def bytes_to_message(data: Buffer) -> Optional["communicator.Message"]:
        """Use MPPMessage deserializer for serializing the message object"""
        if not data:
            return None
        mpp_message = MPPMessage.from_bytes(data)
        return communicator.Message(
            mpp_message.timestamp,
            mpp_message.next_timestamp,
            mpp_message.data,
            mpp_message.settings_overlay,
        )


@dataclass
class SnapshotMetadata:
    """Metadata of a snapshot for sending to the muscle_manager."""

    triggers: list[str]
    wallclock_time: float
    timestamp: float
    next_timestamp: Optional[float]
    port_message_counts: dict[str, list[int]]
    is_final_snapshot: bool
    # storing as str, because Path cannot be serialized by msgpack
    snapshot_filename: str

    @staticmethod
    def from_snapshot(snapshot: Snapshot, snapshot_filename: str) -> "SnapshotMetadata":
        """Create snapshot metadata from the given snapshot and filename"""
        return SnapshotMetadata(
            snapshot.triggers,
            snapshot.wallclock_time,
            snapshot.message.timestamp if snapshot.message else float("NaN"),
            snapshot.message.next_timestamp if snapshot.message else None,
            snapshot.communicator_state.port_message_counts,
            snapshot.is_final_snapshot,
            snapshot_filename,
        )
