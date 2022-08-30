from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, List, Optional, cast

import msgpack

if TYPE_CHECKING:
    # prevent circular import
    from libmuscle.communicator import Message


class Snapshot(ABC):
    """Snapshot data structure.

    This is an abstract base class, implementations are provided by subclasses.
    """
    SNAPSHOT_VERSION_BYTE = b'\0'

    def __init__(self,
                 triggers: List[str],
                 wallclocktime: float,
                 port_message_counts: Dict[str, List[int]],
                 is_final_snapshot: bool,
                 message: 'Message') -> None:
        self.triggers = triggers
        self.wallclocktime = wallclocktime
        self.port_message_counts = port_message_counts
        self.is_final_snapshot = is_final_snapshot
        self.message = message

    @classmethod
    @abstractmethod
    def from_bytes(cls, data: bytes) -> 'Snapshot':
        """Create a snapshot object from binary data.

        Args:
            data: binary data representing the snapshot. Note that this must
                **exclude** the versioning byte.
        """
        ...

    @abstractmethod
    def to_bytes(self) -> bytes:
        """Convert the snapshot object to binary data.

        Returns:
            Binary data representing the snapshot. Note that this must
                **exclude** the versioning byte.
        """
        ...


class MsgPackSnapshot(Snapshot):
    """Snapshot stored in messagepack format
    """
    SNAPSHOT_VERSION_BYTE = b'1'

    @classmethod
    def from_bytes(cls, data: bytes) -> 'Snapshot':
        dct = msgpack.loads(data)
        return cls(dct['triggers'],
                   dct['wallclocktime'],
                   dct['port_message_counts'],
                   dct['is_final_snapshot'],
                   dct['message'])

    def to_bytes(self) -> bytes:
        return cast(bytes, msgpack.dumps({
            'triggers': self.triggers,
            'wallclocktime': self.wallclocktime,
            'port_message_counts': self.port_message_counts,
            'is_final_snapshot': self.is_final_snapshot,
            'message': self.message
        }))


@dataclass
class SnapshotMetadata:
    """Metadata of a snapshot for sending to the muscle_manager.
    """
    triggers: List[str]
    wallclocktime: float
    timestamp: float
    next_timestamp: Optional[float]
    port_message_counts: Dict[str, List[int]]
    is_final_snapshot: bool
    # storing as str, because Path cannot be serialized by msgpack
    snapshot_filename: str

    @staticmethod
    def from_snapshot(snapshot: Snapshot, snapshot_filename: str
                      ) -> 'SnapshotMetadata':
        """Create snapshot metadata from the given snapshot and filename
        """
        return SnapshotMetadata(
            snapshot.triggers,
            snapshot.wallclocktime,
            snapshot.message.timestamp,
            snapshot.message.next_timestamp,
            snapshot.port_message_counts,
            snapshot.is_final_snapshot,
            snapshot_filename
        )
