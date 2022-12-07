from pathlib import Path
import sqlite3
import threading
from typing import Iterable, Optional, Tuple

from libmuscle.profiling import ProfileEvent, ProfileEventType
from ymmsl import Operator, Reference


class ProfileDatabase:
    """Creates and updates a profiling database.

    This class creates the database, and then allow writing to it. It
    should be changed in concert with ProfileDatabase to ensure the
    data format remains in sync.
    """
    def __init__(self, db_file: Path) -> None:
        """Create a new profile database.

        Args:
            db_file: The file to create and initialise.
        """
        if db_file.exists():
            # TODO: maybe allow multiple objects to open the same file?
            raise RuntimeError(f'File {db_file} exists, not overwriting it.')

        # Exactly how the sqlite3 Python module's automatic
        # transactions work is a bit mysterious, and the documentation
        # of sqlite itself isn't perfect either. So we set
        # isolation_level to None, which doesn't actually affect the
        # effective isolation level (!) but does keep the Python module
        # from starting transactions automatically, and then we use
        # explicit BEGIN TRANSACTION statements to keep the sqlite
        # library from doing anything automatically. That way, it's
        # clear what's going on from the code.
        #
        # Also, connections are expensive and cannot be used in other
        # threads. We have a multithreaded TCP server in the manager,
        # so we use thread-local storage to get a connection in each
        # thread.
        self._db_file = db_file

        self._local = threading.local()
        self._local.conn = sqlite3.connect(db_file, isolation_level=None)

        cur = self._local.conn.cursor()
        cur.execute("BEGIN IMMEDIATE TRANSACTION")
        cur.execute(
                "CREATE TABLE muscle3_format ("
                "    major_version INTEGER NOT NULL,"
                "    minor_version INTEGER NOT NULL)")
        cur.execute(
                "INSERT INTO muscle3_format(major_version, minor_version)"
                "    VALUES (1, 0)")

        cur.execute(
                "CREATE TABLE event_types ("
                "    oid INTEGER PRIMARY KEY,"
                "    name TEXT UNIQUE)")
        event_types = [(t.value, t.name) for t in ProfileEventType]
        cur.executemany(
                "INSERT INTO event_types (oid, name) VALUES (?, ?)",
                event_types)

        cur.execute(
                "CREATE TABLE port_operators ("
                "    oid INTEGER PRIMARY KEY,"
                "    name TEXT UNIQUE)")
        port_operators = [(o.value, o.name) for o in Operator]
        cur.executemany(
                "INSERT INTO port_operators (oid, name) VALUES (?, ?)",
                port_operators)

        cur.execute(
                "CREATE TABLE instances ("
                "    oid INTEGER PRIMARY KEY,"
                "    name TEXT UNIQUE)")

        cur.execute(
                "CREATE TABLE events ("
                "    instance INTEGER NOT NULL REFERENCES instances(oid),"
                "    event_type INTEGER NOT NULL REFERENCES event_types(oid),"
                "    start_time DOUBLE NOT NULL,"
                "    stop_time DOUBLE NOT NULL,"
                "    port_name TEXT,"
                "    port_operator INTEGER REFERENCES port_operators(oid),"
                "    port_length INTEGER,"
                "    slot INTEGER,"
                "    message_size INTEGER,"
                "    message_timestamp DOUBLE)")

        cur.execute(
                "CREATE VIEW all_events ("
                "    instance, type, start_time, stop_time, port, operator,"
                "    port_length, slot, message_size, message_timestamp)"
                " AS SELECT"
                "    i.name, et.name, e.start_time, e.stop_time, e.port_name,"
                "    o.name, e.port_length, e.slot, e.message_size,"
                "    e.message_timestamp"
                " FROM"
                "    events e"
                "    JOIN instances i ON e.instance = i.oid"
                "    LEFT JOIN event_types et ON e.event_type = et.oid"
                "    LEFT JOIN port_operators o ON e.port_operator = o.oid")

        cur.execute("COMMIT")
        cur.close()

    def add_events(
            self, instance_id: Reference, events: Iterable[ProfileEvent]
            ) -> None:
        """Adds profiling events to the database.

        Args:
            events: The events to add.
        """
        if not hasattr(self._local, 'conn'):
            self._local.conn = sqlite3.connect(
                    self._db_file, isolation_level=None)
        cur = self._local.conn.cursor()
        cur.execute("BEGIN IMMEDIATE TRANSACTION")
        cur.execute(
                "SELECT oid FROM instances WHERE name = ?",
                (str(instance_id),))
        oids = cur.fetchall()
        if oids:
            instance_oid = oids[0][0]
        else:
            cur.execute(
                    "INSERT INTO instances (name) VALUES (?) RETURNING oid",
                    (str(instance_id),))
            instance_oid = cur.fetchone()[0]

        Record = Tuple[
                int, int, float, float, Optional[str], Optional[int],
                Optional[int], Optional[int], Optional[int],
                Optional[float]]

        def to_tuple(e: ProfileEvent) -> Record:
            # Tell mypy this shouldn't happen
            assert e.start_time is not None
            assert e.stop_time is not None

            port_name = None if e.port is None else str(e.port.name)
            port_operator = None if e.port is None else e.port.operator.value

            return (
                    instance_oid, e.event_type.value, e.start_time.seconds,
                    e.stop_time.seconds, port_name, port_operator,
                    e.port_length, e.slot, e.message_size, e.message_timestamp)

        cur.executemany(
                "INSERT INTO events"
                " (instance, event_type, start_time, stop_time, port_name,"
                "  port_operator, port_length, slot, message_size,"
                "  message_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                list(map(to_tuple, events)))
        cur.execute("COMMIT")
        cur.close()

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
