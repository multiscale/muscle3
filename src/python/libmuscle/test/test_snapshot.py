import pytest
from ymmsl.v0_2 import Settings

from libmuscle.communicator import Message
from libmuscle.communicator_state import CommunicatorState
from libmuscle.snapshot import Snapshot, SnapshotMetadata


@pytest.fixture
def snapshot(communicator_state: CommunicatorState) -> Snapshot:
    triggers = ["test triggers"]
    wallclock_time = 15.3
    is_final = True
    message = Message(1.2, data="test_data")
    snapshot = Snapshot(
        triggers,
        wallclock_time,
        is_final,
        message,
        Settings({"test": 1}),
        communicator_state,
    )
    assert snapshot.triggers == triggers
    assert snapshot.wallclock_time == wallclock_time
    assert snapshot.is_final_snapshot == is_final
    assert snapshot.message == message
    assert snapshot.settings_overlay.keys() == {"test"}
    assert snapshot.settings_overlay["test"] == 1
    return snapshot


def test_snapshot(snapshot: Snapshot) -> None:
    assert isinstance(snapshot, Snapshot)

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = Snapshot.from_bytes(binary_snapshot)

    assert snapshot2.triggers == snapshot.triggers
    assert snapshot2.wallclock_time == snapshot.wallclock_time
    assert snapshot2.is_final_snapshot == snapshot.is_final_snapshot
    assert snapshot2.message.timestamp == snapshot.message.timestamp
    assert snapshot2.message.next_timestamp == snapshot.message.next_timestamp
    assert snapshot2.message.data == snapshot.message.data
    assert snapshot2.communicator_state == snapshot.communicator_state


def test_snapshot_metadata(snapshot: Snapshot) -> None:
    metadata = SnapshotMetadata.from_snapshot(snapshot, "test")

    assert metadata.triggers == snapshot.triggers
    assert metadata.wallclock_time == snapshot.wallclock_time
    assert (
        metadata.port_message_counts == snapshot.communicator_state.port_message_counts
    )
    assert metadata.is_final_snapshot == snapshot.is_final_snapshot
    assert metadata.timestamp == snapshot.message.timestamp
    assert metadata.next_timestamp == snapshot.message.next_timestamp
    assert metadata.snapshot_filename == "test"


def test_message_with_settings(communicator_state: CommunicatorState) -> None:
    message = Message(1.0, 2.0, "test_data", Settings({"setting": True}))
    snapshot = Snapshot([], 0, False, message, Settings(), communicator_state)
    assert snapshot.message.settings.get("setting") is True

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = Snapshot.from_bytes(binary_snapshot)
    assert snapshot2.message.settings.get("setting") is True


def test_implicit_snapshot(communicator_state: CommunicatorState) -> None:
    message = None
    snapshot = Snapshot([], 0, True, message, Settings(), communicator_state)
    assert snapshot.message is None

    binary_snapshot = snapshot.to_bytes()
    assert isinstance(binary_snapshot, bytes)

    snapshot2 = Snapshot.from_bytes(binary_snapshot)
    assert snapshot2.message is None
