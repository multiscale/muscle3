from unittest.mock import patch

from libmuscle.manager.profile_database import ProfileDatabase
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.planner.planner import ResourceAssignment
from libmuscle.profiling import (
        ProfileEvent, ProfileEventType, ProfileTimestamp)

from libmuscle.test.conftest import on_node_resources as onr

from ymmsl import Operator, Port, Reference

import pytest

from pathlib import Path


@pytest.fixture
def db_file(tmp_path) -> Path:
    with patch('libmuscle.manager.profile_store._SYNCHED', True):
        store = ProfileStore(tmp_path)
        t1 = ProfileTimestamp()

        store.store_instances([Reference('instance1'), Reference('instance2')])

        resources1 = ResourceAssignment([
            onr('node001', {0, 1}), onr('node002', {0, 1})])

        resources2 = ResourceAssignment([
            onr('node001', {0}), onr('node002', {0, 1, 2})])

        store.store_resources({
            Reference('instance1'): resources1,
            Reference('instance2'): resources2})

        def t(offset: int) -> ProfileTimestamp:
            return ProfileTimestamp(t1.nanoseconds + offset)

        e1 = [
                ProfileEvent(ProfileEventType.REGISTER, t(0), t(1000)),
                ProfileEvent(ProfileEventType.CONNECT, t(1000), t(2000)),
                ProfileEvent(
                    ProfileEventType.SEND, t(2000), t(2100),
                    Port('out', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.SEND, t(2200), t(2400),
                    Port('out', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.SEND, t(2600), t(2900),
                    Port('out', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(ProfileEventType.SHUTDOWN_WAIT, t(10000), t(11000)),
                ProfileEvent(ProfileEventType.DEREGISTER, t(11000), t(11100))]

        store.add_events(Reference('instance1'), e1)

        e2 = [
                ProfileEvent(ProfileEventType.REGISTER, t(0), t(800)),
                ProfileEvent(ProfileEventType.CONNECT, t(800), t(1600)),
                ProfileEvent(
                    ProfileEventType.RECEIVE, t(2000), t(2100),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.RECEIVE_WAIT, t(2000), t(2090),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.RECEIVE, t(2200), t(2400),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.RECEIVE_WAIT, t(2200), t(2380),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.RECEIVE, t(2600), t(2900),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(
                    ProfileEventType.RECEIVE_WAIT, t(2600), t(2870),
                    Port('in', Operator.O_I), None, None, 1000000, 0.0),
                ProfileEvent(ProfileEventType.SHUTDOWN_WAIT, t(10000), t(11000)),
                ProfileEvent(ProfileEventType.DEREGISTER, t(11000), t(11100))]

        store.add_events(Reference('instance2'), e2)

        db_file = store._db_file
        store.shutdown()

    return db_file


def test_instance_stats(db_file):
    with ProfileDatabase(db_file) as db:
        instances, run_time, comm_time, wait_time = db.instance_stats()
        assert set(instances) == {'instance1', 'instance2'}
        i1 = instances.index('instance1')
        assert run_time[i1] == pytest.approx(7400.0 * 1e-9)
        assert comm_time[i1] == pytest.approx(600.0 * 1e-9)
        assert wait_time[i1] == 0.0
        i2 = instances.index('instance2')
        assert run_time[i2] == pytest.approx(7800.0 * 1e-9)
        assert comm_time[i2] == pytest.approx(60.0 * 1e-9)
        assert wait_time[i2] == pytest.approx(540.0 * 1e-9)


def test_resource_stats(db_file):
    with ProfileDatabase(db_file) as db:
        stats = db.resource_stats()
        assert set(stats.keys()) == set([
            'node001:0', 'node001:1',
            'node002:0', 'node002:1', 'node002:2'])

        assert stats['node001:0'] == {
                'instance1': 8000.0 * 1e-9,
                'instance2': 7860.0 * 1e-9}

        assert stats['node001:1'] == {
                'instance1': 8000.0 * 1e-9}

        assert stats['node002:0'] == {
                'instance1': 8000.0 * 1e-9,
                'instance2': 7860.0 * 1e-9}

        assert stats['node002:1'] == {
                'instance1': 8000.0 * 1e-9,
                'instance2': 7860.0 * 1e-9}

        assert stats['node002:2'] == {
                'instance2': 7860.0 * 1e-9}


def test_time_taken(db_file):
    with ProfileDatabase(db_file) as db:
        assert 1000.0 == db.time_taken(etype='REGISTER', instance='instance1')
        assert 100.0 == db.time_taken(etype='DEREGISTER')
        assert 11100.0 == db.time_taken(
                etype='REGISTER', instance='instance1', etype2='DEREGISTER')
        assert 10000.0 == db.time_taken(
                etype='REGISTER', instance='instance1', time='stop',
                etype2='DEREGISTER', time2='start')
        assert 200.0 == db.time_taken(etype='SEND')
        assert 200.0 == db.time_taken(etype='DEREGISTER', aggregate='sum')
        assert 600.0 == db.time_taken(etype='SEND', aggregate='sum')
