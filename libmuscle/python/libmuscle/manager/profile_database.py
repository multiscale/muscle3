from collections import defaultdict
from pathlib import Path
import sqlite3
import threading
from types import TracebackType
from typing import Any, cast, Dict, List, Optional, Tuple, Type, Union
from warnings import warn


class ProfileDatabase:
    """Accesses a profiling database.

    This class accesses a MUSCLE3 profiling database and provides basic
    analysis functionality.
    """
    def __init__(self, db_file: Union[str, Path]) -> None:
        """Open a ProfileDatabase.

        This opens the database file and creates a ProfileDatabase
        object that operates on it.

        Note that the connection to the database needs to be closed
        again when done. You should use this as a context manager for
        that, e.g.

        .. code-block:: python

            with ProfileDatabase('performance.sqlite') as db:
                # use db here
        """
        if not isinstance(db_file, Path):
            db_file = Path(db_file)

        self._db_file = db_file
        self._local = threading.local()

        self._smallest_timestamp: Optional[float] = None

    def close(self) -> None:
        """Close the connection to the database.

        This should be called once by each thread that used this
        object before it goes down, so that its connection to the
        database can be closed.

        It is usually better to use this class as a context manager,
        e.g.

        .. code-block:: python

            with ProfileDatabase('performance.sqlite') as db:
                # use db here
        """
        # If the thread never served a request, then we don't have a
        # connection.
        if hasattr(self._local, 'conn'):
            self._local.conn.close()

    def instance_stats(
            self) -> Tuple[List[str], List[float], List[float], List[float]]:
        """Calculate per-instance statistics.

        This calculates the total time spent computing, the total time
        spent communicating, and the total time spent waiting for
        a message to arrive, for each instance, in seconds.

        It returns a tuple of four lists, containing instance names,
        run times, communication times, and wait times. Note that the
        run times do not include data transfer or waiting for messages,
        so these three are exclusive and add up to the total time the
        instance was active.

        Note that sending messages in MUSCLE3 is partially done in the
        background. Transfer times include encoding and queueing of any
        sent messages as well as downloading received messages, but it
        does not include the sending side of the transfer, as this is
        done by a background thread in parallel with other work that is
        recorded (usually waiting, sometimes computing or sending
        another message).

        Nevertheless, this should give you an idea of which instances
        use the most resources. Keep in mind though that different
        instances may use different numbers of cores, so a model that
        doesn't spend much wallclock time may still spend many core
        hours. Secondly, waiting does not necessarily leave a core idle
        as MUSCLE3 is capable of detecting when models will not compute
        at the same time and having them share cores.

        See the profiling documentation page for an example.

        Returns:
            A list of instance names, a corresponding list of compute
            times, a corresponding list of transfer times, and a
            corresponding list of wait times.
        """
        cur = self._get_cursor()
        cur.execute("BEGIN TRANSACTION")
        cur.execute("SELECT name FROM instances")
        instances = [row[0] for row in cur.fetchall()]

        cur.execute(
                "SELECT instance, stop_time"
                " FROM all_events"
                " WHERE type = 'CONNECT'")
        start_run = dict(cur.fetchall())

        for name in instances:
            if name not in start_run:
                warn(
                        f'Instance {name} seems to have never registered with the'
                        ' manager, and will be omitted from the results. Did it crash'
                        ' on startup?')

        cur.execute(
                "SELECT instance, start_time"
                " FROM all_events"
                " WHERE type = 'SHUTDOWN_WAIT'")
        stop_run = dict(cur.fetchall())

        for name in instances:
            if name not in stop_run:
                # instances with no connected f_init ports don't have SHUTDOWN_WAIT
                # try to use the start of DISCONNECT_WAIT instead as the stop time
                cur.execute(
                        "SELECT start_time"
                        " FROM all_events"
                        " WHERE type = 'DISCONNECT_WAIT' and instance = ?", [name])
                result = cur.fetchall()
                if result:
                    stop_run[name] = result[0][0]
                else:
                    # as a last resort, just take the last registered event
                    warn(
                            f'Instance {name} did not shut down cleanly, data may be'
                            ' inaccurate or missing')

                    cur.execute(
                            "SELECT stop_time"
                            " FROM all_events"
                            " WHERE instance = ?"
                            " ORDER BY stop_time DESC LIMIT 1", [name])
                    result = cur.fetchall()
                    if result:
                        stop_run[name] = result[0][0]

        cur.execute(
                "SELECT instance, SUM(stop_time - start_time)"
                " FROM all_events"
                " WHERE type = 'SEND' OR type = 'RECEIVE'"
                " GROUP BY instance")
        comm = dict(cur.fetchall())

        cur.execute(
                "SELECT instance, SUM(stop_time - start_time)"
                " FROM all_events"
                " WHERE type = 'RECEIVE_WAIT'"
                " GROUP BY instance")
        wait = dict(cur.fetchall())

        cur.execute("COMMIT")
        cur.close()

        complete_instances = list(set(start_run) & set(stop_run))

        total_times = [(stop_run[i] - start_run[i]) * 1e-9 for i in complete_instances]
        comm_times = [
                (
                    (comm[i] if i in comm else 0) -
                    (wait[i] if i in wait else 0)
                ) * 1e-9
                for i in complete_instances]
        wait_times = [(wait[i] if i in wait else 0) * 1e-9 for i in complete_instances]
        run_times = [
                t - c - w
                for t, c, w in zip(total_times, comm_times, wait_times)]

        return complete_instances, run_times, comm_times, wait_times

    def resource_stats(self) -> Dict[str, Dict[str, float]]:
        """Calculate per-core statistics.

        This function calculates the amount of time each core has
        spent running each component assigned to it. It returns
        a dictionary indexed by `(node, core)` tuples which contains
        for each core a nested dictionary mapping components to the
        number of seconds that component used that core for. This
        includes time spent calculating and time spent receiving data,
        but not time spent waiting for input.

        Returns:
            A dictionary containing for each (node, core) tuple a
            dictionary containing for each component the total time
            it ran on that core.
        """
        instances, run_times, comm_times, _ = self.instance_stats()

        active_times = {
                i: r + c
                for i, r, c in zip(instances, run_times, comm_times)}

        cur = self._get_cursor()
        cur.execute("BEGIN TRANSACTION")
        cur.execute(
                "SELECT i.name, ac.node, ac.core"
                " FROM instances AS i"
                " JOIN assigned_cores AS ac ON (i.oid = ac.instance_oid)")
        instances_by_core = defaultdict(list)
        for name, node, core in cur.fetchall():
            instances_by_core[':'.join([node, str(core)])].append(name)

        cur.execute("COMMIT")
        cur.close()

        result: Dict[str, Dict[str, float]] = defaultdict(dict)
        for core, instances in instances_by_core.items():
            for instance in instances:
                result[core][instance] = active_times[instance]

        return result

    def time_taken(
            self, *, etype: str, instance: Optional[str] = None,
            port: Optional[str] = None, slot: Optional[int] = None,
            time: Optional[str] = 'start', etype2: Optional[str] = None,
            port2: Optional[str] = None, slot2: Optional[int] = None,
            time2: Optional[str] = 'stop', aggregate: str = 'mean') -> float:
        """Calculate time of and between events.

        This function returns the mean or total time spent on or
        between selected points in time recorded in the database, in
        nanoseconds. Note that due to operating system limitations,
        actual precision for individual measurements is limited to
        about a microsecond.

        For profiling purposes, an event is an operation performed by
        one of the instances in the simulation. It has a type, a
        start time, and a stop time. For example, when an instance
        sends a message, this is recorded as an event of type SEND,
        with associated timestamps. For some events, other information
        may also be recorded, such as the port and slot a message was
        sent or received on, message size, and so on.

        This function takes two points in time, each of which is the
        beginning or the end of a certain kind of event, and
        calculates the time between those two points. For example, to
        calculate how long it takes instance `micro` to send a message
        on port `final_state`, you can do

        .. code-block:: python

            db.time_taken(
                    etype='SEND', instance='micro', port='final_state')

        This selects events of type `SEND`, as well as an instance
        and a port, and since we didn't specify anything else, we get
        the time taken from the beginning to the end of the selected
        event. The `micro` model is likely to have sent many messages,
        and this function will automatically calculate the mean
        duration. So this tells us on average how long it takes
        `micro` to send a message on `final_state`.

        Averaging will be done over all attributes that are not
        specified, so for example if `final_state` is a vector port, then
        the average will be taken over all sends on all slots, unless
        a specific slot is specified by a `slot` argument.

        It is also possible to calculate time between different events.
        For example, if we know that `micro` receives on
        `initial_state`, does some calculations, and then sends on
        `state_out`, and we want to know how long the calculations take,
        then we can use

        .. code-block:: python

            db.time_taken(
                    instance='micro', port='initial_state',
                    etype='RECEIVE', time='stop',
                    port2='final_state', etype2='SEND',
                    time2='start')

        This gives the time between the end of a receive on
        `initial_state` and the start of a subsequent send on
        `final_state`. The arguments with a 2 at the end of their name
        refer to the end of the period we're measuring, and by default
        their value is taken from the corresponding start argument. So,
        the first command is actually equivalent to

        .. code-block:: python

            db.time_taken(
                etype='SEND', instance='micro', port='final_state',
                slot=None, time='start', etype2='SEND',
                port2='final_state', slot2=None, time2='stop')

        which says that we measure the time from the start of each send
        by `micro` on `final_state` to the end of each send on
        `final_state`, aggregating over all slots if applicable.

        Speaking of aggregation, there is a final argument `aggregate`
        which defaults to `mean`, but can be set to `sum` to calculate
        the sum instead. For example:

        .. code-block:: python

            db.time_taken(
                    etype='RECEIVE_WAIT', instance='macro',
                    port='state_in', aggregate='sum')


        gives the total time that `macro` has spent waiting for a
        message to arrive on its `state_in` port.

        If you are taking points in time from different events (e.g.
        different instances, ports, slots or types) then there must be
        the same number of events in the database for the start and
        end event. So starting at the end of `REGISTER` and stopping
        at the beginning of a `SEND` on an `O_I` port will likely not
        work, because the instance only registers once and probably
        sends more than once.

        Args:
            etype: Type of event to get the starting point from.
                Possible values: `'REGISTER'`, `'CONNECT'`, `'SHUTDOWN_WAIT'`,
                `'DISCONNECT_WAIT'`, `'SHUTDOWN'`, `'DEREGISTER'`, `'SEND'`,
                `'RECEIVE'`, `'RECEIVE_WAIT'`, `'RECEIVE_TRANSFER'`,
                `'RECEIVE_DECODE'`. See the documentation for a description
                of each.
            instance: Name of the instance to get the event from. You
                can use `%` as a wildcard matching anything. For
                example, `'macro[%'` will match all instances of the
                `macro` component, if it has many.
            port: Selected port, for send and receive events.
            slot: Selected slot, for send and receive events.
            time: Either `'start'` or `'stop'`, to select the beginning
                or the end of the specified event. Defaults to
                `'start'`.
            etype2: Type of event to get the stopping point from. See
                `etype`. Defaults to the value of `etype`.
            port2: Selected port. See `port`. Defaults to the value of
                `port`.
            slot2: Selected slot. See `slot`. Defaults to the value of
                `slot`.
            time2: Either `'start'` or `'stop'`, to select the
                beginning or the end of the specified event. Defaults
                to `'stop'`.
            aggregate: Either `'mean'` (default) or `'sum'`, to
                calculate that statistic.

        Returns:
            The mean or total time taken in nanoseconds.
        """
        if time is None:
            time = 'start'

        if etype2 is None:
            etype2 = etype

        if port2 is None:
            port2 = port

        if slot2 is None:
            slot2 = slot

        if time2 is None:
            time2 = 'stop'

        if time in ('start', 'stop'):
            timestamp = time + '_time'
        else:
            raise ValueError(
                    'Invalid time value, please specify either "start"'
                    ' or "stop".')

        if time2 in ('start', 'stop'):
            timestamp2 = time2 + '_time'
        else:
            raise ValueError(
                    'Invalid time2 value, please specify either "start"'
                    ' or "stop".')

        # To do sum(stop - start) across different events, we'd have
        # to do an expensive and tricky self-join on the events table
        # because we'd have to find the subsequent event of type 2 to
        # the current event of type 1.
        #
        # So instead, we calculate sum(stop) - sum(start), as well
        # as counts of both to make sure there's the same number and
        # also so we can calculate the average.
        #
        # We don't have enough digits in the timestamps to add up
        # more than a handful of them, so we split them and add the
        # high and low 32-bit halves separately. Note that whether
        # the right shift sign-extends is implementation-defined.
        # It does on almost all modern platforms, and anyway, you'd
        # have to time-travel to before 1970 to notice any problem.

        def get_sum_count(
                cur: sqlite3.Cursor, etype: Optional[str], timestamp: str,
                instance: Optional[str], port: Optional[str],
                slot: Optional[int]) -> Tuple[int, int, int]:
            """Get sums and count for one time point."""
            cur.execute("BEGIN TRANSACTION")
            query = (
                    "SELECT SUM({0} >> 32), SUM({0} & 0xffffffff), COUNT(*)"
                    " FROM all_events"
                    " WHERE type = ?".format(timestamp))
            qargs: List[Any] = [etype]

            if instance is not None:
                query += " AND instance = ?"
                qargs.append(instance)

            if port is not None:
                query += " AND port = ?"
                qargs.append(port)

            if slot is not None:
                query += " AND slot = ?"
                qargs.append(slot)

            cur.execute(query, qargs)
            result = cur.fetchone()
            cur.execute("COMMIT")
            return cast(Tuple[int, int, int], result)

        cur = self._get_cursor()
        sum1_high, sum1_low, count1 = get_sum_count(
                cur, etype, timestamp, instance, port, slot)
        sum2_high, sum2_low, count2 = get_sum_count(
                cur, etype2, timestamp2, instance, port2, slot2)
        cur.close()

        if count1 != count2:
            raise RuntimeError(
                    'The number of start and stop events is not the same:'
                    f' {count1} != {count2}')

        if count1 == 0:
            if aggregate == 'sum':
                return 0.0
            raise RuntimeError('No matching events were found')

        diff_high = (sum2_high - sum1_high) << 32
        diff_low = sum2_low - sum1_low
        if aggregate == 'mean':
            return (diff_high + diff_low) / count1
        elif aggregate == 'sum':
            return diff_high + diff_low
        else:
            raise ValueError(
                    f'Unknown aggregate {aggregate}, please specify either'
                    ' "mean" or "sum"')

    def __enter__(self) -> 'ProfileDatabase':
        return self

    def __exit__(
            self, exc_type: Optional[Type[BaseException]],
            exc_val: Optional[BaseException], exc_tb: Optional[TracebackType]
            ) -> None:
        self.close()

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
