import random
import time

import pytest
from ymmsl import Operator, load, dump

from libmuscle import (
        Instance, Message, KEEPS_NO_STATE_FOR_NEXT_USE, USES_CHECKPOINT_API,
        SKIP_MMSF_SEQUENCE_CHECKS)
from libmuscle.manager.run_dir import RunDir

from .conftest import run_manager_with_actors, ls_snapshots


_LOG_LEVEL = 'INFO'  # set to DEBUG for additional debug info


def cache_component(max_channels=2):
    ports = {Operator.F_INIT: [f'in{i+1}' for i in range(max_channels)],
             Operator.O_I: [f'sub_out{i+1}' for i in range(max_channels)],
             Operator.S: [f'sub_in{i+1}' for i in range(max_channels)],
             Operator.O_F: [f'out{i+1}' for i in range(max_channels)]}
    instance = Instance(ports, USES_CHECKPOINT_API)

    cache_t = float('-inf')
    cache_data = []
    max_cache_age = None
    nil_msg = Message(0.0)

    while instance.reuse_instance():
        if instance.resuming():
            instance.load_snapshot()

        if instance.should_init():
            cache_valid_range = instance.get_setting('cache_valid', '[float]')
            if max_cache_age is None:
                max_cache_age = random.uniform(*cache_valid_range)

            msgs = [instance.receive(port, default=nil_msg)
                    for port in ports[Operator.F_INIT]]
            cur_t = msgs[0].timestamp

        if cur_t - cache_t >= max_cache_age:
            # Cached value is no longer valid, run submodel for updated data
            for msg, port in zip(msgs, ports[Operator.O_I]):
                instance.send(port, Message(cur_t, data=msg.data))
            cache_data = [instance.receive(port, default=nil_msg).data
                          for port in ports[Operator.S]]
            cache_t = cur_t
            max_cache_age = random.uniform(*cache_valid_range)

        for data, port in zip(cache_data, ports[Operator.O_F]):
            instance.send(port, Message(cur_t, data=data))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(cur_t, data=[]))


def echo_component(max_channels=2):
    ports = {Operator.F_INIT: [f'in{i+1}' for i in range(max_channels)],
             Operator.O_F: [f'out{i+1}' for i in range(max_channels)]}
    instance = Instance(ports, KEEPS_NO_STATE_FOR_NEXT_USE | SKIP_MMSF_SEQUENCE_CHECKS)

    while instance.reuse_instance():
        for p_in, p_out in zip(ports[Operator.F_INIT], ports[Operator.O_F]):
            if instance.is_connected(p_in):
                instance.send(p_out, instance.receive(p_in))


def main_component():
    instance = Instance({
            Operator.O_I: ['state_out'],
            Operator.S: ['Ai', 'Bi', 'Ci', 'Di'],
            Operator.O_F: ['o_f']}, USES_CHECKPOINT_API)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            t_cur = msg.timestamp
            i, t_remaining = msg.data
            monotonic_end = time.monotonic() + t_remaining

        if instance.should_init():
            t_cur = 0
            monotonic_end = time.monotonic() + t_max
            i = 0

        while time.monotonic() < monotonic_end:
            instance.send('state_out', Message(t_cur, data=i))
            for port in ('Ai', 'Bi', 'Ci', 'Di'):
                instance.receive(port)

            t_cur += dt
            i += 1
            time.sleep(0.05)

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(
                        t_cur, data=[i, monotonic_end - time.monotonic()]))

        instance.send('o_f', Message(t_cur, data=i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, data=[i, 0]))


@pytest.fixture
def config():
    return load(f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    main: main_component
    cacheA: cache_component
    cacheB: cache_component
    cacheC: cache_component
    calcA: echo_component
    calcB: echo_component
    calcC: echo_component
    calcD: echo_component
  conduits:
    main.state_out:
    - cacheA.in1
    - cacheB.in1
    - cacheC.in1
    - calcD.in1

    cacheA.out1: main.Ai
    cacheA.out2: main.Bi
    cacheA.sub_out1: calcA.in1
    cacheA.sub_out2: calcA.in2
    calcA.out1: cacheA.sub_in1
    calcA.out2: cacheA.sub_in2

    cacheB.out1:
    - cacheA.in2
    - cacheC.in2
    cacheB.sub_out1: calcB.in1
    calcB.out1: cacheB.sub_in1

    cacheC.out1: main.Ci
    cacheC.sub_out1: calcC.in1
    cacheC.sub_out2: calcC.in2
    calcC.out1: cacheC.sub_in1

    calcD.out1: main.Di

settings:
  dt: 1.234
  t_max: 1.8  # seconds
  cacheA.cache_valid: [2.0, 5.0]
  cacheB.cache_valid: [3.0, 8.0]
  cacheC.cache_valid: [4.0, 10.0]
  muscle_remote_log_level: {_LOG_LEVEL}
checkpoints:
  at_end: true
  wallclock_time:
  - every: 0.5""")


def test_snapshot_complex_coupling(tmp_path, config):
    actors = {'main': ('python', main_component)}
    for c in 'ABC':
        actors['cache' + c] = ('python', cache_component)
    for c in 'ABCD':
        actors['calc' + c] = ('python', echo_component)

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(dump(config), run_dir1.path, actors)

    # Note: snapshotting based on wallclock time is less reliable, and depending on
    # many factors (OS load, machine speed, etc.) different amounts of snapshots may be
    # created with each run of this test. Asserts only check that at least 1 exists,
    # even though we expect more
    assert len(ls_snapshots(run_dir1, 'main')) >= 1
    assert len(ls_snapshots(run_dir1, 'cacheA')) >= 1
    assert len(ls_snapshots(run_dir1, 'cacheB')) >= 1
    assert len(ls_snapshots(run_dir1, 'cacheC')) >= 1
    assert len(ls_snapshots(run_dir1, 'calcA')) >= 1
    assert len(ls_snapshots(run_dir1, 'calcB')) >= 1
    assert len(ls_snapshots(run_dir1, 'calcC')) >= 1
    assert len(ls_snapshots(run_dir1, 'calcD')) >= 1

    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) >= 1
