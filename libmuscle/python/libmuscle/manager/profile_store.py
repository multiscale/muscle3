import logging
from pathlib import Path
import sqlite3
from typing import Iterable, Optional, Tuple

from libmuscle.profiling import ProfileEvent, ProfileEventType
from libmuscle.manager.profile_database import ProfileDatabase
from ymmsl import Operator, Reference


_logger = logging.getLogger(__name__)


class ProfileStore(ProfileDatabase):
    """Creates and fills a profiling database.

    This class creates the database, and then allows writing to it.
    It's only used internally, and it's almost a non-const version
    of ProfileDatabase.
    """
    def __init__(self, db_dir: Path) -> None:
        """Create a new profile database.

        Args:
            db_file: The file to create and initialise.
        """
        db_file = db_dir / 'performance.sqlite'

        if db_file.exists():
            _logger.info(f'Overwriting profiling database {db_file}')
            try:
                # from Python 3.8, we can use missing_ok=True
                db_file.unlink()
            except FileNotFoundError:
                pass

        super().__init__(db_file)
        self._init_database()

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

    def _init_database(self) -> None:
        """Initialises the database.

        This creates the SQL tables needed to store the data.
        """
        cur = self._get_cursor()
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
