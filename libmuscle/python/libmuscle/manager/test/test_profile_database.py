from libmuscle.profiling import ProfileEvent, ProfileEventType
from libmuscle.manager.profile_database import ProfileDatabase
from libmuscle.timestamp import Timestamp
from ymmsl import Operator, Port, Reference

import sqlite3


def test_create_profile_database(tmp_path):
    db_path = tmp_path / 'test.db'
    db = ProfileDatabase(db_path)
    db.close()

    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()
    cur.execute("BEGIN TRANSACTION")
    cur.execute("SELECT major_version, minor_version FROM muscle3_format")
    major, minor = cur.fetchone()
    assert major == 1
    assert minor == 0

    cur.execute("SELECT oid, name FROM event_types")
    etypes = cur.fetchall()
    assert len(etypes) == len([e for e in ProfileEventType])

    cur.execute("SELECT oid, name FROM port_operators")
    opers = cur.fetchall()
    assert len(opers) == len([o for o in Operator])

    cur.execute("SELECT oid, name FROM instances")
    instances = cur.fetchall()
    assert len(instances) == 0

    cur.execute(
            "SELECT instance, event_type, start_time, stop_time, port_name,"
            "       port_operator, port_length, slot, message_size,"
            "       message_timestamp FROM events")
    events = cur.fetchall()
    assert len(events) == 0

    cur.execute("COMMIT")
    cur.close()
    conn.close()


def test_add_events(tmp_path):
    db_path = tmp_path / 'test.db'
    db = ProfileDatabase(db_path)
    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()

    events = [
            ProfileEvent(
                ProfileEventType.REGISTER, Timestamp(0.0), Timestamp(0.1)),
            ProfileEvent(
                ProfileEventType.SEND, Timestamp(0.8), Timestamp(0.812),
                Port('out_port', Operator.O_I), 10, 3, 12345, 13.42),
            ProfileEvent(
                ProfileEventType.DEREGISTER, Timestamp(1.0), Timestamp(1.1))]

    def check_send_event(instance):
        cur.execute("BEGIN TRANSACTION")
        cur.execute(
                "SELECT *"
                " FROM events AS e, instances AS i, event_types AS et,"
                "      port_operators AS o"
                " WHERE e.instance = i.oid AND e.event_type = et.oid"
                " AND e.port_operator = o.oid AND i.name = 'instance[0]'"
                " AND et.name = (?)", (ProfileEventType.SEND.name,))
        events2 = cur.fetchall()

        assert len(events2) == 1
        e = events2[0]
        assert e[1:10] == (
                ProfileEventType.SEND.value, 0.8, 0.812, 'out_port',
                Operator.O_I.value, 10, 3, 12345, 13.42)
        assert e[11] == 'instance[0]'
        assert e[13] == 'SEND'
        assert e[15] == 'O_I'

        cur.execute("COMMIT")

    db.add_events(Reference('instance[0]'), events)
    check_send_event('instance[0]')

    db.add_events(Reference('instance[1]'), events)
    check_send_event('instance[1]')

    def check_register_event(typ, start, stop):
        cur.execute("BEGIN TRANSACTION")
        cur.execute(
                "SELECT i.name, e.start_time, e.stop_time"
                " FROM events AS e, instances AS i, event_types AS et"
                " WHERE e.instance = i.oid AND e.event_type = et.oid"
                f" AND et.name = '{typ}'")

        events2 = cur.fetchall()
        cur.execute("COMMIT")

        assert len(events2) == 2
        assert set(events2) == {
                ('instance[0]', start, stop), ('instance[1]', start, stop)}

    check_register_event('REGISTER', 0.0, 0.1)
    check_register_event('DEREGISTER', 1.0, 1.1)

    cur.close()
    conn.close()
    db.close()
