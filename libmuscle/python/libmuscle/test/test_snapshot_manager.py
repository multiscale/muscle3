from datetime import datetime, timezone
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from ymmsl import (
        Reference, Checkpoints, CheckpointRangeRule, ImplementationState)

from libmuscle.communicator import Message
from libmuscle.snapshot import SnapshotMetadata
from libmuscle.snapshot_manager import SnapshotManager


def test_no_checkpointing(caplog: pytest.LogCaptureFixture, tmp_path: Path
                          ) -> None:
    manager = MagicMock()
    communicator = MagicMock()
    communicator.get_message_counts.return_value = {}
    snapshot_manager = SnapshotManager(
            Reference('test'), manager, communicator,
            ImplementationState.STATEFUL)

    snapshot_manager._set_checkpoint_info(
            datetime.now(timezone.utc), Checkpoints(), None)

    assert not snapshot_manager.resuming()
    snapshot_manager.reuse_instance(tmp_path, True, None)
    assert not snapshot_manager.resuming()
    assert not snapshot_manager.should_save_snapshot(1)
    assert not snapshot_manager.should_save_snapshot(5000)
    assert not snapshot_manager.should_save_final_snapshot(False, None)

    with caplog.at_level(logging.INFO, 'libmuscle'):
        snapshot_manager.save_snapshot(Message(1.0, None, None))
        assert caplog.records[0].levelname == "INFO"
        assert "no checkpoints" in caplog.records[0].message


def test_save_load_snapshot(tmp_path: Path) -> None:
    manager = MagicMock()
    communicator = MagicMock()
    port_message_counts = {'in': [1], 'out': [2], 'muscle_settings_in': [0]}
    communicator.get_message_counts.return_value = port_message_counts

    instance_id = Reference('test[1]')
    snapshot_manager = SnapshotManager(
            instance_id, manager, communicator, ImplementationState.STATEFUL)

    checkpoints = Checkpoints(simulation_time=[CheckpointRangeRule(every=1)])
    snapshot_manager._set_checkpoint_info(
            datetime.now(timezone.utc), checkpoints, None)

    assert not snapshot_manager.resuming()
    snapshot_manager.reuse_instance(tmp_path, True, None)
    with pytest.raises(RuntimeError):
        snapshot_manager.load_snapshot()

    assert not snapshot_manager.resuming()
    assert snapshot_manager.should_save_snapshot(0.2)
    snapshot_manager.save_snapshot(Message(0.2, None, 'test data'))

    communicator.get_message_counts.assert_called_with()
    manager.submit_snapshot_metadata.assert_called()
    instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    assert instance == instance_id
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers
    assert metadata.wallclock_time > 0.0
    assert metadata.timestamp == 0.2
    assert metadata.next_timestamp is None
    assert metadata.port_message_counts == port_message_counts
    assert not metadata.is_final_snapshot
    snapshot_path = Path(metadata.snapshot_filename)
    assert snapshot_path.parent == tmp_path
    assert snapshot_path.name == 'test-1_1.pack'

    snapshot_manager2 = SnapshotManager(
            instance_id, manager, communicator, ImplementationState.STATEFUL)

    snapshot_manager2._set_checkpoint_info(
            datetime.now(timezone.utc), checkpoints, snapshot_path)
    communicator.restore_message_counts.assert_called_with(port_message_counts)

    assert snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(tmp_path, True, None)
    assert snapshot_manager2.resuming()
    msg = snapshot_manager2.load_snapshot()
    assert msg.timestamp == 0.2
    assert msg.next_timestamp is None
    assert msg.data == 'test data'

    assert not snapshot_manager2.should_save_snapshot(0.4)
    assert snapshot_manager2.should_save_final_snapshot(True, 1.2)
    snapshot_manager2.save_final_snapshot(
            Message(0.6, None, 'test data2'), 1.2)

    instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    assert instance == instance_id
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers
    assert metadata.wallclock_time > 0.0
    assert metadata.timestamp == 0.6
    assert metadata.next_timestamp is None
    assert metadata.port_message_counts == port_message_counts
    assert metadata.is_final_snapshot
    snapshot_path = Path(metadata.snapshot_filename)
    assert snapshot_path.parent == tmp_path
    assert snapshot_path.name == 'test-1_2.pack'

    assert snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(tmp_path, True, None)
    assert not snapshot_manager2.resuming()


def test_save_load_implicit_snapshot(tmp_path: Path) -> None:
    manager = MagicMock()
    communicator = MagicMock()
    port_message_counts = {'in': [1], 'out': [2], 'muscle_settings_in': [0]}
    communicator.get_message_counts.return_value = port_message_counts

    instance_id = Reference('test[1]')
    snapshot_manager = SnapshotManager(
            instance_id, manager, communicator, ImplementationState.STATELESS)

    checkpoints = Checkpoints(simulation_time=[CheckpointRangeRule(every=1)])
    snapshot_manager._set_checkpoint_info(
            datetime.now(timezone.utc), checkpoints, None)

    assert not snapshot_manager.resuming()
    snapshot_manager.reuse_instance(tmp_path, True, None)
    snapshot_manager.reuse_instance(tmp_path, True, 1.5)
    manager.submit_snapshot_metadata.assert_called_once()
    instance, metadata = manager.submit_snapshot_metadata.call_args[0]
    assert instance == instance_id
    assert isinstance(metadata, SnapshotMetadata)
    snapshot_path = Path(metadata.snapshot_filename)
    manager.submit_snapshot_metadata.reset_mock()

    snapshot_manager2 = SnapshotManager(
            instance_id, manager, communicator, ImplementationState.STATELESS)

    snapshot_manager2._set_checkpoint_info(
            datetime.now(timezone.utc), checkpoints, snapshot_path)
    communicator.restore_message_counts.assert_called_with(port_message_counts)

    assert not snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(tmp_path, True, 1.5)
    assert not snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(tmp_path, True, 2.5)
    manager.submit_snapshot_metadata.assert_called_once()
