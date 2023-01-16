from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, cast

import msgpack
from ymmsl import Reference, Settings

from libmuscle.mpp_message import MPPMessage
from libmuscle import communicator


class Snapshot(ABC):
    """Snapshot data structure.

    This is an abstract base class, implementations are provided by subclasses.
    """
    SNAPSHOT_VERSION_BYTE = b'\0'

    def __init__(self,
                 triggers: List[str],
                 wallclock_time: float,
                 port_message_counts: Dict[str, List[int]],
                 is_final_snapshot: bool,
                 message: Optional['communicator.Message'],
                 settings_overlay: Settings) -> None:
        self.triggers = triggers
        self.wallclock_time = wallclock_time
        self.port_message_counts = port_message_counts
        self.is_final_snapshot = is_final_snapshot
        self.message = message
        # self.message is None for implicit snapshots, so we cannot store the
        # Settings overlay in that message object.
        self.settings_overlay = settings_overlay

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
                   dct['wallclock_time'],
                   dct['port_message_counts'],
                   dct['is_final_snapshot'],
                   cls.bytes_to_message(dct['message']),
                   Settings(dct['settings_overlay']))

    def to_bytes(self) -> bytes:
        return cast(bytes, msgpack.dumps({
            'triggers': self.triggers,
            'wallclock_time': self.wallclock_time,
            'port_message_counts': self.port_message_counts,
            'is_final_snapshot': self.is_final_snapshot,
            'message': self.message_to_bytes(self.message),
            'settings_overlay': self.settings_overlay.as_ordered_dict()
        }))

    @staticmethod
    def message_to_bytes(message: Optional['communicator.Message']) -> bytes:
        """Use MPPMessage serializer for serializing the message object
        """
        if message is None:
            return b''
        settings = Settings()
        if message.settings is not None:
            settings = message.settings
        return MPPMessage(Reference('_'), Reference('_'), None,
                          message.timestamp, message.next_timestamp,
                          settings, 0, -1.0, message.data).encoded()

    @staticmethod
    def bytes_to_message(data: bytes) -> Optional['communicator.Message']:
        """Use MPPMessage deserializer for serializing the message object
        """
        if not data:
            return None
        mpp_message = MPPMessage.from_bytes(data)
        return communicator.Message(mpp_message.timestamp,
                                    mpp_message.next_timestamp,
                                    mpp_message.data,
                                    mpp_message.settings_overlay)


@dataclass
class SnapshotMetadata:
    """Metadata of a snapshot for sending to the muscle_manager.
    """
    triggers: List[str]
    wallclock_time: float
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
            snapshot.wallclock_time,
            snapshot.message.timestamp if snapshot.message else float('NaN'),
            snapshot.message.next_timestamp if snapshot.message else None,
            snapshot.port_message_counts,
            snapshot.is_final_snapshot,
            snapshot_filename
        )
