import logging
from pathlib import Path
from typing import cast, List, Optional

from ymmsl import Reference, Operator, Settings

from libmuscle.communicator import Message
from libmuscle.port_manager import PortManager
from libmuscle.mmp_client import MMPClient
from libmuscle.snapshot import MsgPackSnapshot, Snapshot, SnapshotMetadata

_logger = logging.getLogger(__name__)

_MAX_FILE_EXISTS_CHECK = 10000

# error text for save_snapshot when msg = None
_NO_MESSAGE_PROVIDED = (
        'Invalid message provided to `{}`. Please create a Message object to'
        ' store the state of the instance in a snapshot.')


class SnapshotManager:
    """Manages information on snapshots for the Instance

    Implements the saving and loading of snapshots in the checkpointing API.
    """

    def __init__(
            self, instance_id: Reference, manager: MMPClient,
            port_manager: PortManager) -> None:
        """Create a new snapshot manager

        Args:
            instance_id: The id of this instance.
            manager: The client used to submit data to the manager.
            port_manager: The port manager belonging to this instance.
        """
        self._instance_id = instance_id
        # replace identifier[i] by identifier-i to use in snapshot file name
        # using a dash (-) because that is not allowed in Identifiers
        self._safe_id = str(instance_id).replace("[", "-").replace("]", "")
        self._port_manager = port_manager
        self._manager = manager

        self._resume_from_snapshot: Optional[Snapshot] = None
        self.resume_overlay: Optional[Settings] = None
        self._next_snapshot_num = 1

    def prepare_resume(
            self, resume_snapshot: Optional[Path],
            snapshot_directory: Optional[Path]) -> Optional[float]:
        """Apply checkpoint info received from the manager.

        If there is a snapshot to resume from, this loads it and does
        any resume work that libmuscle should do, including restoring
        message counts and storing the resumed-from snapshot again as
        our first snapshot.

        Args:
            resume_snapshot: Snapshot to resume from (or None if not
                resuming)
            snapshot_directory: directory to save snapshots in

        Returns:
            Time at which the initial snapshot was saved, if resuming.
        """
        result: Optional[float] = None
        self._snapshot_directory = snapshot_directory or Path.cwd()
        if resume_snapshot is not None:
            snapshot = self.load_snapshot_from_file(resume_snapshot)

            if snapshot.message is not None:
                # snapshot.message is None for implicit snapshots
                self._resume_from_snapshot = snapshot
                result = snapshot.message.timestamp
            self.resume_overlay = snapshot.settings_overlay

            self._port_manager.restore_message_counts(snapshot.port_message_counts)
            # Store a copy of the snapshot in the current run directory
            path = self.__store_snapshot(snapshot)
            metadata = SnapshotMetadata.from_snapshot(snapshot, str(path))
            self._manager.submit_snapshot_metadata(metadata)

        return result

    def resuming_from_intermediate(self) -> bool:
        """Check whether we have an intermediate snapshot.

        Doesn't say whether we should resume now, just that we were
        given an intermediate snapshot to resume from by the manager.
        """
        return (
                self._resume_from_snapshot is not None and
                not self._resume_from_snapshot.is_final_snapshot)

    def resuming_from_final(self) -> bool:
        """Check whether we have a final snapshot.

        Doesn't say whether we should resume now, just that we were
        given an intermediate snapshot to resume from by the manager.
        """
        return (
                self._resume_from_snapshot is not None and
                self._resume_from_snapshot.is_final_snapshot)

    def load_snapshot(self) -> Message:
        """Get the Message to resume from.
        """
        snapshot = cast(Snapshot, self._resume_from_snapshot)
        return cast(Message, snapshot.message)

    def save_snapshot(
            self, msg: Optional[Message], final: bool,
            triggers: List[str], wallclock_time: float,
            f_init_max_timestamp: Optional[float],
            settings_overlay: Settings
            ) -> float:
        """Save a (final) snapshot.

        Args:
            msg: Message object representing the snapshot.
            final: True iff called from save_final_snapshot.
            triggers: Description of checkpoints that triggered this.
            wallclock_time: Wallclock time when saving.
            f_init_max_timestamp: Timestamp for final snapshots.
            settings_overlay: Current settings overlay.

        Returns:
            Simulation time at which the snapshot was made.
        """
        port_message_counts = self._port_manager.get_message_counts()
        if final:
            # Decrease F_INIT port counts by one: F_INIT messages are already
            # pre-received, but not yet processed by the user code. Therefore,
            # the snapshot state should treat these as not-received.
            all_ports = self._port_manager.list_ports()
            ports = all_ports.get(Operator.F_INIT, [])
            if self._port_manager.settings_in_connected():
                ports.append('muscle_settings_in')
            for port_name in ports:
                new_counts = [i - 1 for i in port_message_counts[port_name]]
                port_message_counts[port_name] = new_counts

        snapshot = MsgPackSnapshot(
                triggers, wallclock_time, port_message_counts, final, msg,
                settings_overlay)

        path = self.__store_snapshot(snapshot)
        metadata = SnapshotMetadata.from_snapshot(snapshot, str(path))
        self._manager.submit_snapshot_metadata(metadata)

        timestamp = msg.timestamp if msg is not None else float('-inf')
        if final and f_init_max_timestamp is not None:
            # For final snapshots f_init_max_snapshot is the reference time (see
            # should_save_final_snapshot).
            timestamp = f_init_max_timestamp
        return timestamp

    @staticmethod
    def load_snapshot_from_file(snapshot_location: Path) -> Snapshot:
        """Load a previously stored snapshot from the filesystem.

        Args:
            snapshot_location: path where the snapshot is stored.
        """
        _logger.debug(f'Loading snapshot from {snapshot_location}')
        if not snapshot_location.is_file():
            raise RuntimeError(f'Unable to load snapshot: {snapshot_location}'
                               ' is not a file. Please ensure this path exists'
                               ' and can be read.')

        # TODO: encapsulate I/O errors?
        with snapshot_location.open('rb') as snapshot_file:
            version = snapshot_file.read(1)
            data = snapshot_file.read()

            if version == MsgPackSnapshot.SNAPSHOT_VERSION_BYTE:
                return MsgPackSnapshot.from_bytes(data)
            raise RuntimeError('Unable to load snapshot from'
                               f' {snapshot_location}: unknown version of'
                               ' snapshot file. Was the file saved with a'
                               ' different version of libmuscle or'
                               ' edited?')

    def __store_snapshot(self, snapshot: Snapshot) -> Path:
        """Store a snapshot on the filesystem.

        Args:
            snapshot: Snapshot to store.

        Returns:
            Path where the snapshot is stored.
        """
        _logger.debug(f'Saving snapshot to {self._snapshot_directory}')
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
