from pathlib import Path
from typing import Iterable

from libmuscle.profiling import ProfileEvent
from libmuscle.manager.profile_database import ProfileDatabase
from ymmsl import Reference


class ProfileStore:
    """Stores profiling information to disk."""
    def __init__(self, log_dir: Path) -> None:
        """Create a ProfileStore.

        This will save the recorded profiling data to a file named
        ``performance.sqlite`` in the main RunDir.

        Args:
            log_dir: Directory to store the database in
        """
        db_file = log_dir / 'performance.sqlite'
        self._db = ProfileDatabase(db_file)

    def add_events(
            self, instance_id: Reference, events: Iterable[ProfileEvent]
            ) -> None:
        """Adds profiling events to the database.

        Args:
            events: The events to add.
        """
        self._db.add_events(instance_id, events)

    def close(self) -> None:
        """Close the store.

        This should be called once by each thread that used this
        object before it goes down, so that its connection to the
        database can be closed.
        """
        self._db.close()
