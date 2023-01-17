import pytest
from ymmsl import Settings

from libmuscle.communicator import Message
from libmuscle.snapshot import Snapshot, MsgPackSnapshot, SnapshotMetadata


@pytest.fixture
def snapshot() -> Snapshot:
    triggers = ['test triggers']
    wallclock_time = 15.3
    port_message_counts = {'in': [1], 'out': [4], 'muscle_settings_in': [0]}
    is_final = True
    message = Message(1.2, data='test_data')
    snapshot = MsgPackSnapshot(
            triggers, wallclock_time, port_message_counts, is_final, message,
            Settings({'test': 1}))
    assert snapshot.triggers == triggers
    assert snapshot.wallclock_time == wallclock_time
    assert snapshot.port_message_counts == port_message_counts
    assert snapshot.is_final_snapshot == is_final
    assert snapshot.message == message
    assert snapshot.settings_overlay.keys() == {'test'}
    assert snapshot.settings_overlay['test'] == 1
    return snapshot


def test_snapshot(snapshot: Snapshot) -> None:
    assert isinstance(snapshot, Snapshot)

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = MsgPackSnapshot.from_bytes(binary_snapshot)

    assert snapshot2.triggers == snapshot.triggers
    assert snapshot2.wallclock_time == snapshot.wallclock_time
    assert snapshot2.port_message_counts == snapshot.port_message_counts
    assert snapshot2.is_final_snapshot == snapshot.is_final_snapshot
    assert snapshot2.message.timestamp == snapshot.message.timestamp
    assert snapshot2.message.next_timestamp == snapshot.message.next_timestamp
    assert snapshot2.message.data == snapshot.message.data


def test_snapshot_metadata(snapshot: Snapshot) -> None:
    metadata = SnapshotMetadata.from_snapshot(snapshot, 'test')

    assert metadata.triggers == snapshot.triggers
    assert metadata.wallclock_time == snapshot.wallclock_time
    assert metadata.port_message_counts == snapshot.port_message_counts
    assert metadata.is_final_snapshot == snapshot.is_final_snapshot
    assert metadata.timestamp == snapshot.message.timestamp
    assert metadata.next_timestamp == snapshot.message.next_timestamp
    assert metadata.snapshot_filename == 'test'


def test_message_with_settings() -> None:
    message = Message(1.0, 2.0, 'test_data', Settings({'setting': True}))
    snapshot = MsgPackSnapshot([], 0, {}, False, message, Settings())
    assert snapshot.message.settings.get('setting') is True

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = MsgPackSnapshot.from_bytes(binary_snapshot)
    assert snapshot2.message.settings.get('setting') is True


def test_implicit_snapshot() -> None:
    message = None
    snapshot = MsgPackSnapshot([], 0, {}, True, message, Settings())
    assert snapshot.message is None

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = MsgPackSnapshot.from_bytes(binary_snapshot)
    assert snapshot2.message is None
