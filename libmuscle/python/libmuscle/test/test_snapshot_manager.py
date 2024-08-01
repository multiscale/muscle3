from pathlib import Path
from unittest.mock import MagicMock

from ymmsl import Reference, Settings

from libmuscle.communicator import Message
from libmuscle.snapshot import SnapshotMetadata
from libmuscle.snapshot_manager import SnapshotManager


def test_no_checkpointing(tmp_path: Path) -> None:
    manager = MagicMock()
    port_manager = MagicMock()
    port_manager.get_message_counts.return_value = {}
    snapshot_manager = SnapshotManager(Reference('test'), manager, port_manager)

    snapshot_manager.prepare_resume(None, tmp_path)
    assert not snapshot_manager.resuming_from_intermediate()
    assert not snapshot_manager.resuming_from_final()


def test_save_load_snapshot(tmp_path: Path) -> None:
    manager = MagicMock()
    port_manager = MagicMock()
    port_message_counts = {'in': [1], 'out': [2], 'muscle_settings_in': [0]}
    port_manager.get_message_counts.return_value = port_message_counts

    instance_id = Reference('test[1]')
    snapshot_manager = SnapshotManager(instance_id, manager, port_manager)

    snapshot_manager.prepare_resume(None, tmp_path)
    assert not snapshot_manager.resuming_from_intermediate()
    assert not snapshot_manager.resuming_from_final()

    snapshot_manager.save_snapshot(
            Message(0.2, None, 'test data'), False, ['test'], 13.0, None,
            Settings())

    port_manager.get_message_counts.assert_called_with()
    manager.submit_snapshot_metadata.assert_called()
    metadata, = manager.submit_snapshot_metadata.call_args[0]
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers == ['test']
    assert metadata.wallclock_time == 13.0
    assert metadata.timestamp == 0.2
    assert metadata.next_timestamp is None
    assert metadata.port_message_counts == port_message_counts
    assert not metadata.is_final_snapshot
    snapshot_path = Path(metadata.snapshot_filename)
    assert snapshot_path.parent == tmp_path
    assert snapshot_path.name == 'test-1_1.pack'

    snapshot_manager2 = SnapshotManager(instance_id, manager, port_manager)

    snapshot_manager2.prepare_resume(snapshot_path, tmp_path)
    port_manager.restore_message_counts.assert_called_with(port_message_counts)

    assert snapshot_manager2.resuming_from_intermediate()
    assert not snapshot_manager2.resuming_from_final()
    msg = snapshot_manager2.load_snapshot()
    assert msg.timestamp == 0.2
    assert msg.next_timestamp is None
    assert msg.data == 'test data'

    snapshot_manager2.save_snapshot(
            Message(0.6, None, 'test data2'), True, ['test'], 42.2, 1.2,
            Settings())

    metadata, = manager.submit_snapshot_metadata.call_args[0]
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers == ['test']
    assert metadata.wallclock_time == 42.2
    assert metadata.timestamp == 0.6
    assert metadata.next_timestamp is None
    assert metadata.port_message_counts == port_message_counts
    assert metadata.is_final_snapshot
    snapshot_path = Path(metadata.snapshot_filename)
    assert snapshot_path.parent == tmp_path
    assert snapshot_path.name == 'test-1_3.pack'


def test_save_load_implicit_snapshot(tmp_path: Path) -> None:
    manager = MagicMock()
    port_manager = MagicMock()
    port_message_counts = {'in': [1], 'out': [2], 'muscle_settings_in': [0]}
    port_manager.get_message_counts.return_value = port_message_counts

    instance_id = Reference('test[1]')
    snapshot_manager = SnapshotManager(instance_id, manager, port_manager)

    snapshot_manager.prepare_resume(None, tmp_path)

    assert not snapshot_manager.resuming_from_intermediate()
    assert not snapshot_manager.resuming_from_final()
    # save implicit snapshot
    snapshot_manager.save_snapshot(
            None, True, ['implicit'], 1.0, 1.5, Settings())

    manager.submit_snapshot_metadata.assert_called_once()
    metadata, = manager.submit_snapshot_metadata.call_args[0]
    assert isinstance(metadata, SnapshotMetadata)
    snapshot_path = Path(metadata.snapshot_filename)
    manager.submit_snapshot_metadata.reset_mock()

    snapshot_manager2 = SnapshotManager(instance_id, manager, port_manager)

    snapshot_manager2.prepare_resume(snapshot_path, tmp_path)
    port_manager.restore_message_counts.assert_called_with(port_message_counts)
    manager.submit_snapshot_metadata.assert_called_once()
    manager.submit_snapshot_metadata.reset_mock()

    assert not snapshot_manager2.resuming_from_intermediate()
    assert not snapshot_manager2.resuming_from_final()
    snapshot_manager2.save_snapshot(
            None, True, ['implicit'], 12.3, 2.5, Settings())
    manager.submit_snapshot_metadata.assert_called_once()
