from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)
from libmuscle.manager.profile_store import ProfileStore
from ymmsl import Operator, Port, Reference

import sqlite3
from unittest.mock import patch


def test_create_profile_store(tmp_path):
    db = ProfileStore(tmp_path)
    db.shutdown()

    db_path = tmp_path / 'performance.sqlite'
    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()
    cur.execute("BEGIN TRANSACTION")
    cur.execute("SELECT major_version, minor_version FROM muscle3_format")
    major, minor = cur.fetchone()
    assert major == 1
    assert minor == 1

    cur.execute("SELECT oid, name FROM event_types")
    etypes = cur.fetchall()
    assert len(etypes) == len(ProfileEventType)

    cur.execute("SELECT oid, name FROM port_operators")
    opers = cur.fetchall()
    assert len(opers) == len(Operator)

    cur.execute("SELECT oid, name FROM instances")
    instances = cur.fetchall()
    assert len(instances) == 0

    cur.execute(
            "SELECT instance_oid, event_type_oid, start_time, stop_time, port_name,"
            "       port_operator_oid, port_length, slot, message_number, message_size,"
            "       message_timestamp FROM events")
    events = cur.fetchall()
    assert len(events) == 0

    cur.execute("COMMIT")
    cur.close()
    conn.close()


@patch('libmuscle.manager.profile_store._SYNCHED', True)
def test_add_events(tmp_path):
    db = ProfileStore(tmp_path)

    db_path = tmp_path / 'performance.sqlite'
    conn = sqlite3.connect(db_path, isolation_level=None)
    cur = conn.cursor()

    events = [
            ProfileEvent(
                ProfileEventType.REGISTER, ProfileTimestamp(0),
                ProfileTimestamp(1000)),
            ProfileEvent(
                ProfileEventType.SEND, ProfileTimestamp(800),
                ProfileTimestamp(812),
                Port('out_port', Operator.O_I), 10, 3, 67, 12345, 13.42),
            ProfileEvent(
                ProfileEventType.DEREGISTER, ProfileTimestamp(1000000000000),
                ProfileTimestamp(1100000000000))]

    def check_send_event(instance):
        cur.execute("BEGIN TRANSACTION")
        cur.execute(
                "SELECT *"
                " FROM events AS e, instances AS i, event_types AS et,"
                "      port_operators AS o"
                " WHERE e.instance_oid = i.oid AND e.event_type_oid = et.oid"
                " AND e.port_operator_oid = o.oid AND i.name = 'instance[0]'"
                " AND et.name = (?)", (ProfileEventType.SEND.name,))
        events2 = cur.fetchall()

        assert len(events2) == 1
        e = events2[0]
        assert e[1:11] == (
                ProfileEventType.SEND.value, 800, 812, 'out_port',
                Operator.O_I.value, 10, 3, 67, 12345, 13.42)
        assert e[12] == 'instance[0]'
        assert e[14] == 'SEND'
        assert e[16] == 'O_I'

        cur.execute("COMMIT")

    db.store_instances([Reference('instance[0]'), Reference('instance[1]')])

    db.add_events(Reference('instance[0]'), events)
    check_send_event('instance[0]')

    db.add_events(Reference('instance[1]'), events)
    check_send_event('instance[1]')

    def check_register_event(typ, start, stop):
        cur.execute("BEGIN TRANSACTION")
        cur.execute(
                "SELECT i.name, e.start_time, e.stop_time"
                " FROM events AS e, instances AS i, event_types AS et"
                " WHERE e.instance_oid = i.oid AND e.event_type_oid = et.oid"
                " AND et.name = ?", (typ,))

        events2 = cur.fetchall()
        cur.execute("COMMIT")

        assert len(events2) == 2
        assert set(events2) == {
                ('instance[0]', start, stop), ('instance[1]', start, stop)}

    check_register_event('REGISTER', 0, 1000)
    check_register_event('DEREGISTER', 1000000000000, 1100000000000)

    cur.close()
    conn.close()
    db.shutdown()
