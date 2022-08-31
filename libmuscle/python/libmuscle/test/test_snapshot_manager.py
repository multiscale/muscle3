from datetime import datetime, timezone
import logging
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from ymmsl import Reference, Checkpoints, CheckpointRules

from libmuscle.communicator import Message
from libmuscle.snapshot import SnapshotMetadata
from libmuscle.snapshot_manager import SnapshotManager


def test_no_checkpointing(caplog: pytest.LogCaptureFixture, tmp_path: Path
                          ) -> None:
    manager = MagicMock()
    communicator = MagicMock()
    communicator.get_message_counts.return_value = {}
    snapshot_manager = SnapshotManager(Reference('test'), manager, communicator)

    snapshot_manager.registered(datetime.now(timezone.utc), Checkpoints(), None)

    snapshot_manager.reuse_instance(None, Path(tmp_path))
    assert not snapshot_manager.resuming()
    assert not snapshot_manager.should_save_snapshot(1, None)
    assert not snapshot_manager.should_save_snapshot(5000, None)
    assert not snapshot_manager.should_save_final_snapshot(1000)

    with caplog.at_level(logging.INFO, 'libmuscle.snapshot_manager'):
        snapshot_manager.save_snapshot(Message(1.0, None, None))
        assert caplog.records[0].levelname == "INFO"
        assert "no checkpoints" in caplog.records[0].message


def test_save_load_checkpoint(tmp_path: Path) -> None:
    manager = MagicMock()
    communicator = MagicMock()
    port_message_counts = {'in': [1], 'out': [2], 'muscle_settings_in': [0]}
    communicator.get_message_counts.return_value = port_message_counts

    instance_id = Reference('test[1]')
    snapshot_manager = SnapshotManager(instance_id, manager, communicator)

    checkpoints = Checkpoints(simulation_time=CheckpointRules(every=1))
    snapshot_manager.registered(datetime.now(timezone.utc), checkpoints, None)

    snapshot_manager.reuse_instance(None, tmp_path)
    with pytest.raises(RuntimeError):
        snapshot_manager.load_snapshot()

    assert not snapshot_manager.resuming()
    assert snapshot_manager.should_save_snapshot(0.2, 0.4)
    snapshot_manager.save_snapshot(Message(0.2, 0.4, 'test data'))

    communicator.get_message_counts.assert_called_with()
    manager.submit_snapshot_metadata.assert_called()
    metadata = manager.submit_snapshot_metadata.call_args[0][0]
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers
    assert metadata.wallclock_time > 0.0
    assert metadata.timestamp == 0.2
    assert metadata.next_timestamp == 0.4
    assert metadata.port_message_counts == port_message_counts
    assert not metadata.is_final_snapshot
    fpath = Path(metadata.snapshot_filename)
    assert fpath.parent == tmp_path
    assert fpath.name == 'test-1_1.pack'

    snapshot_manager2 = SnapshotManager(instance_id, manager, communicator)

    snapshot_manager2.registered(datetime.now(timezone.utc), checkpoints, fpath)
    communicator.restore_message_counts.assert_called_with(port_message_counts)

    assert snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(None, tmp_path)
    assert snapshot_manager2.resuming()
    msg = snapshot_manager2.load_snapshot()
    assert msg.timestamp == 0.2
    assert msg.next_timestamp == 0.4
    assert msg.data == 'test data'

    assert not snapshot_manager2.should_save_snapshot(0.4, 0.6)
    assert snapshot_manager2.should_save_final_snapshot(0.6)
    snapshot_manager2.save_final_snapshot(Message(0.6, None, 'test data2'))

    metadata = manager.submit_snapshot_metadata.call_args[0][0]
    assert isinstance(metadata, SnapshotMetadata)
    assert metadata.triggers
    assert metadata.wallclock_time > 0.0
    assert metadata.timestamp == 0.6
    assert metadata.next_timestamp is None
    assert metadata.port_message_counts == port_message_counts
    assert metadata.is_final_snapshot
    fpath = Path(metadata.snapshot_filename)
    assert fpath.parent == tmp_path
    assert fpath.name == 'test-1_2.pack'

    assert snapshot_manager2.resuming()
    snapshot_manager2.reuse_instance(None, tmp_path)
    assert not snapshot_manager2.resuming()
