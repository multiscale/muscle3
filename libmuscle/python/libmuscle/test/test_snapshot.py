import pytest

from libmuscle.communicator import Message
from libmuscle.snapshot import Snapshot, MsgPackSnapshot, SnapshotMetadata


@pytest.fixture
def snapshot() -> Snapshot:
    triggers = ["test triggers"]
    wallclocktime = 15.3
    port_message_counts = {'in': [1], 'out': [4], 'muscle_settings_in': [0]}
    is_final = True
    message = Message(1.2, None, "test_data")
    snapshot = MsgPackSnapshot(
            triggers, wallclocktime, port_message_counts, is_final, message)
    assert snapshot.triggers == triggers
    assert snapshot.wallclocktime == wallclocktime
    assert snapshot.port_message_counts == port_message_counts
    assert snapshot.is_final_snapshot == is_final
    assert snapshot.message == message
    return snapshot


def test_snapshot(snapshot: Snapshot) -> None:
    assert isinstance(snapshot, Snapshot)

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = MsgPackSnapshot.from_bytes(binary_snapshot)

    assert snapshot2.triggers == snapshot.triggers
    assert snapshot2.wallclocktime == snapshot.wallclocktime
    assert snapshot2.port_message_counts == snapshot.port_message_counts
    assert snapshot2.is_final_snapshot == snapshot.is_final_snapshot
    assert snapshot2.message.timestamp == snapshot.message.timestamp
    assert snapshot2.message.next_timestamp == snapshot.message.next_timestamp
    assert snapshot2.message.data == snapshot.message.data


def test_snapshot_metadata(snapshot: Snapshot) -> None:
    metadata = SnapshotMetadata.from_snapshot(snapshot, "test")

    assert metadata.triggers == snapshot.triggers
    assert metadata.wallclocktime == snapshot.wallclocktime
    assert metadata.port_message_counts == snapshot.port_message_counts
    assert metadata.is_final_snapshot == snapshot.is_final_snapshot
    assert metadata.timestamp == snapshot.message.timestamp
    assert metadata.next_timestamp == snapshot.message.next_timestamp
    assert metadata.snapshot_filename == "test"
