import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, cast

from ymmsl import Checkpoints, Reference

from libmuscle.checkpoint_triggers import TriggerManager
from libmuscle.communicator import Communicator, Message
from libmuscle.mmp_client import MMPClient
from libmuscle.snapshot import MsgPackSnapshot, Snapshot, SnapshotMetadata

_logger = logging.getLogger(__name__)

_MAX_FILE_EXISTS_CHECK = 10000


class SnapshotManager:
    """Manages information on snapshots for the Instance

    Implements the public checkpointing API with handoffs to
    :class:`TriggerManager` for checkpoint triggers.
    """

    def __init__(self,
                 instance_id: Reference,
                 manager: MMPClient,
                 communicator: Communicator) -> None:
        """Create a new snapshot manager

        Args:
            instance_id: The id of this instance.
            manager: The client used to submit data to the manager.
            communicator: The communicator belonging to this instance.
        """
        self._instance_id = instance_id
        # replace identifier[i] by identifier-i to use in snapshot file name
        # using a dash (-) because that is not allowed in Identifiers
        self._safe_id = str(instance_id).replace("[", "-").replace("]", "")
        self._communicator = communicator
        self._manager = manager

        self._first_reuse = True
        self._trigger = TriggerManager()
        self._resume_from_snapshot = None   # type: Optional[Snapshot]
        self._snapshot_directory = None     # type: Optional[Path]
        self._next_snapshot_num = 1

    def set_checkpoint_info(self,
                            utc_reference: datetime,
                            checkpoints: Checkpoints,
                            resume: Optional[Path]) -> None:
        """Callback after registering with the manager.

        Provide the snapshot manager with info on workflow checkpoints and if we
        should resume from a previous snapshot.

        Args:
            utc_reference: datetime (in UTC) indicating wallclock_time=0
            checkpoints: requested workflow checkpoints
            resume: previous snapshot to resume from (or None if not resuming)
        """
        self._trigger.set_checkpoint_info(utc_reference, checkpoints)
        if resume is not None:
            self.__load_snapshot(resume)
            snapshot = cast(Snapshot, self._resume_from_snapshot)
            self._communicator.restore_message_counts(
                snapshot.port_message_counts)
            self._trigger.update_checkpoints(
                snapshot.message.timestamp,
                snapshot.is_final_snapshot)

    def reuse_instance(self, snapshot_directory: Optional[Path]) -> None:
        """Callback on Instance.reuse_instance

        Args:
            snapshot_directory: Path to store this instance's snapshots in.
        """
        self._trigger.reuse_instance()

        self._snapshot_directory = snapshot_directory

        if self._first_reuse:
            self._first_reuse = False
        else:
            self._resume_from_snapshot = None

    def resuming(self) -> bool:
        """Check if we are resuming during this reuse iteration.
        """
        return self._resume_from_snapshot is not None

    def should_init(self) -> bool:
        """Check if F_INIT should be run in this reuse loop.

        Returns:
            True: when not resuming this reuse loop, or when resuming from a
                final snapshot.
            False: otherwise
        """
        return (self._resume_from_snapshot is None or
                self._resume_from_snapshot.is_final_snapshot)

    def load_snapshot(self) -> Message:
        """Get the Message to resume from
        """
        if self._resume_from_snapshot is None:
            raise RuntimeError('No snapshot to load. Use "instance.resuming()"'
                               ' to check if a snapshot is available')
        return self._resume_from_snapshot.message

    def should_save_snapshot(self, timestamp: float) -> bool:
        """See :meth:`TriggerManager.should_save_snapshot`
        """
        return self._trigger.should_save_snapshot(timestamp)

    def should_save_final_snapshot(
            self, do_reuse: bool,
            f_init_max_timestamp: Optional[float]
            ) -> bool:
        """See :meth:`TriggerManager.should_save_final_snapshot`
        """
        return self._trigger.should_save_final_snapshot()

    def save_snapshot(self, msg: Message) -> None:
        """Save snapshot contained in the message object.
        """
        self.__save_snapshot(msg, False)

    def save_final_snapshot(self, msg: Message) -> None:
        """Save final snapshot contained in the message object
        """
        self.__save_snapshot(msg, True)

    def __save_snapshot(self, msg: Message, final: bool) -> None:
        """Actual implementation used by save_(final_)snapshot.

        Args:
            msg: message object representing the snapshot
            final: True iff called from save_final_snapshot
        """
        triggers = self._trigger.get_triggers()
        wallclock_time = self._trigger.elapsed_walltime()

        port_message_counts = self._communicator.get_message_counts()
        snapshot = MsgPackSnapshot(
            triggers, wallclock_time, port_message_counts, final, msg)

        path = self.__store_snapshot(snapshot)
        metadata = SnapshotMetadata.from_snapshot(snapshot, str(path))
        self._manager.submit_snapshot_metadata(self._instance_id, metadata)

        self._trigger.update_checkpoints(msg.timestamp, final)

    def __load_snapshot(self, snapshot_location: Path) -> None:
        """Load a previously stored snapshot from the filesystem

        Args:
            snapshot_location: path where the snapshot is stored
        """
        if not snapshot_location.is_file():
            raise RuntimeError(f'Unable to load snapshot: {snapshot_location}'
                               ' is not a file. Please ensure this path exists'
                               ' and can be read.')

        # TODO: encapsulate I/O errors?
        with snapshot_location.open('rb') as snapshot_file:
            version = snapshot_file.read(1)
            data = snapshot_file.read()

            if version == MsgPackSnapshot.SNAPSHOT_VERSION_BYTE:
                self._resume_from_snapshot = MsgPackSnapshot.from_bytes(data)
            else:
                raise RuntimeError('Unable to load snapshot from'
                                   f' {snapshot_location}: unknown version of'
                                   ' snapshot file. Was the file saved with a'
                                   ' different version of libmuscle or'
                                   ' tampered with?')

    def __store_snapshot(self, snapshot: Snapshot) -> Path:
        """Store a snapshot on the filesystem

        Args:
            snapshot: snapshot to store

        Returns:
            Path where the snapshot is stored
        """
        if self._snapshot_directory is None:
            raise RuntimeError('Unknown snapshot directory. Did you try to'
                               ' save a snapshot before entering the reuse'
                               ' loop?')
        for _ in range(_MAX_FILE_EXISTS_CHECK):
            # Expectation is that muscle_snapshot_directory is empty initially
            # and we succeed in the first loop. Still wrapping in a for-loop
            # such that an existing filename doesn't immediately raise an error
            fname = f"{self._safe_id}_{self._next_snapshot_num}.pack"
            fpath = self._snapshot_directory / fname
            self._next_snapshot_num += 1
            if not fpath.exists():
                break
        else:
            raise RuntimeError('Could not find an available filename for'
                               f' storing the next snapshot: {fpath} already'
                               ' exists.')
        # Opening with mode 'x' since a file with the same name may be created
        # in the small window between checking above and opening here. It is
        # better to fail with an error than to overwrite an existing file.
        with fpath.open('xb') as snapshot_file:
            snapshot_file.write(snapshot.SNAPSHOT_VERSION_BYTE)
            snapshot_file.write(snapshot.to_bytes())
        return fpath
