import logging
from pathlib import Path
from queue import Queue
from sqlite3 import Cursor
from threading import Thread
from typing import cast, Dict, Iterable, List, Optional, Tuple

from libmuscle.planner.planner import ResourceAssignment
from libmuscle.profiling import ProfileEvent, ProfileEventType
from libmuscle.manager.profile_database import ProfileDatabase
from ymmsl import Operator, Reference


_logger = logging.getLogger(__name__)


# When True causes add_events to return after the data is written.
# Used for testing only.
_SYNCHED = False


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

        # 500 batches is about 250MB
        Item = Optional[Tuple[Reference, Iterable[ProfileEvent]]]
        self._queue: Queue[Item] = Queue(500)
        self._confirmation_queue: Queue[None] = Queue()
        self._thread = Thread(target=self._storage_thread, daemon=True)
        self._thread.start()

    def shutdown(self) -> None:
        """Shut down the profile store.

        This closes the database connection cleanly.
        """
        self._queue.put(None)
        self._thread.join()
        super().close()

    def store_instances(
            self, instances: List[Reference]) -> None:
        """Store names of instances in the simulation.

        Args:
            instances: List of instance names to store
        """
        cur = self._get_cursor()
        cur.execute("BEGIN IMMEDIATE TRANSACTION")

        cur.executemany(
                "INSERT INTO instances (name) VALUES (?)",
                [(str(name),) for name in instances])
        cur.execute("COMMIT")
        cur.close()

    def store_resources(self, resources: Dict[Reference, ResourceAssignment]) -> None:
        """Store resource assignments into the database.

        Args:
            resources: The resources to store.
        """
        cur = self._get_cursor()
        cur.execute("BEGIN IMMEDIATE TRANSACTION")

        for instance_id, res in resources.items():
            instance_oid = self._get_instance_oid(cur, instance_id)

            tuples = [
                    (instance_oid, node.node_name, core.cid)
                    for node in res.as_resources()
                    for core in node.cpu_cores]

            cur.executemany(
                    "INSERT INTO assigned_cores (instance_oid, node, core)"
                    " VALUES (?, ?, ?)",
                    tuples)

        cur.execute("COMMIT")
        cur.close()

    def add_events(
            self, instance_id: Reference, events: Iterable[ProfileEvent]
            ) -> None:
        """Adds profiling events to the database.

        Args:
            events: The events to add.
        """
        self._queue.put((instance_id, events))
        if _SYNCHED:
            self._confirmation_queue.get()

    def _storage_thread(self) -> None:
        """Background thread that stores the data.

        We're getting issues with the database being locked occasionally
        on slow file systems when we try to access it from multiple
        threads. So we use a single background thread now to do the
        writing.
        """
        Record = Tuple[
                int, int, float, float, Optional[str], Optional[int],
                Optional[int], Optional[int], Optional[int], Optional[int],
                Optional[float]]

        def to_tuple(e: ProfileEvent) -> Record:
            # Tell mypy this shouldn't happen
            assert e.start_time is not None
            assert e.stop_time is not None

            port_name = None if e.port is None else str(e.port.name)
            port_operator = None if e.port is None else e.port.operator.value

            return (
                    instance_oid, e.event_type.value, e.start_time.nanoseconds,
                    e.stop_time.nanoseconds, port_name, port_operator,
                    e.port_length, e.slot, e.message_number, e.message_size,
                    e.message_timestamp)

        cur = self._get_cursor()
        batch = self._queue.get()
        while batch is not None:
            instance_id, events = batch

            cur = self._get_cursor()
            cur.execute("BEGIN IMMEDIATE TRANSACTION")

            instance_oid = self._get_instance_oid(cur, instance_id)

            cur.executemany(
                    "INSERT INTO events"
                    " (instance_oid, event_type_oid, start_time, stop_time,"
                    "  port_name, port_operator_oid, port_length, slot,"
                    "  message_number, message_size, message_timestamp)"
                    " VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    map(to_tuple, events))
            cur.execute("COMMIT")
            if _SYNCHED:
                self._confirmation_queue.put(None)
            batch = self._queue.get()

        cur.close()
        super().close()

    def _get_instance_oid(self, cur: Cursor, instance_id: Reference) -> int:
        """Get the oid for a given instance.

        Args:
            instance Instance id to look up

        Return:
            The oid used for it in the database
        """
        cur.execute(
                "SELECT oid FROM instances WHERE name = ?",
                (str(instance_id),))
        oids = cur.fetchall()
        return cast(int, oids[0][0])

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
                "    VALUES (1, 1)")

        cur.execute(
                "CREATE TABLE instances ("
                "    oid INTEGER PRIMARY KEY,"
                "    name TEXT UNIQUE)")

        cur.execute(
                "CREATE TABLE assigned_cores ("
                "    instance_oid INTEGER NOT NULL REFERENCES instances(oid),"
                "    node TEXT NOT NULL,"
                "    core INTEGER NOT NULL)")

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
                "CREATE TABLE events ("
                "    instance_oid INTEGER NOT NULL REFERENCES instances(oid),"
                "    event_type_oid INTEGER NOT NULL REFERENCES event_types(oid),"
                "    start_time INTEGER NOT NULL,"
                "    stop_time INTEGER NOT NULL,"
                "    port_name TEXT,"
                "    port_operator_oid INTEGER REFERENCES port_operators(oid),"
                "    port_length INTEGER,"
                "    slot INTEGER,"
                "    message_number INTEGER,"
                "    message_size INTEGER,"
                "    message_timestamp DOUBLE)")

        cur.execute("CREATE INDEX instances_oid_idx ON instances(oid)")

        cur.execute("CREATE INDEX events_start_time_idx ON events(start_time)")

        cur.execute(
                "CREATE VIEW all_events"
                " AS SELECT"
                "    i.name AS instance, et.name AS type,"
                "    e.start_time AS start_time, e.stop_time AS stop_time,"
                "    e.port_name AS port, o.name AS operator,"
                "    e.port_length AS port_length, e.slot AS slot,"
                "    e.message_number AS message_number,"
                "    e.message_size AS message_size,"
                "    e.message_timestamp AS message_timestamp"
                " FROM"
                "    events e"
                "    JOIN instances i ON e.instance_oid = i.oid"
                "    LEFT JOIN event_types et ON e.event_type_oid = et.oid"
                "    LEFT JOIN port_operators o ON e.port_operator_oid = o.oid")

        cur.execute("COMMIT")
        cur.close()
