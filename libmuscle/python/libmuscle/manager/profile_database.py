from pathlib import Path
import sqlite3
import threading
from typing import cast


class ProfileDatabase:
    """Accesses a profiling database.

    This class accesses a MUSCLE3 profiling database and provides basic
    analysis functionality.
    """
    def __init__(self, db_file: Path) -> None:
        """Open a ProfileDatabase.

        This opens the database file and creates a ProfileDatabase
        object that operates on it.
        """
        self._db_file = db_file
        self._local = threading.local()

    def close(self) -> None:
        """Close the connection to the database.

        This should be called once by each thread that used this
        object before it goes down, so that its connection to the
        database can be closed.
        """
        # If the thread never served a request, then we don't have a
        # connection.
        if hasattr(self._local, 'conn'):
            self._local.conn.close()

    def _get_cursor(self) -> sqlite3.Cursor:
        """Get a connection to run queries with.

        Exactly how the sqlite3 Python module's automatic
        transactions work is a bit mysterious, and the documentation
        of sqlite itself isn't perfect either. So we set
        isolation_level to None, which doesn't actually affect the
        effective isolation level (!) but does keep the Python module
        from starting transactions automatically, and then we use
        explicit BEGIN TRANSACTION statements to keep the sqlite
        library from doing anything automatically. That way, it's
        clear what's going on from the code.

        Also, connections are expensive and cannot be used in other
        threads. We have a multithreaded TCP server in the manager,
        so we use thread-local storage to get a connection in each
        thread.
        """
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                    self._db_file, isolation_level=None)
        return cast(sqlite3.Cursor, self._local.conn.cursor())
