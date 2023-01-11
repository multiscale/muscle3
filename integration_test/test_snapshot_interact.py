import logging
import sys
from pathlib import Path

import pytest
from ymmsl import Operator, load, dump

from libmuscle import Instance, Message
from libmuscle.manager.run_dir import RunDir

from .conftest import run_manager_with_actors, ls_snapshots

# Make interact_coupling.py available (from docs/sources/examples)
sys.path.append(str(
        Path(__file__).parents[1] / 'docs' / 'source' / 'examples' / 'python'))
import interact_coupling  # noqa

_LOG_LEVEL = 'INFO'  # set to DEBUG for additional debug info


def component():
    instance = Instance({
            Operator.O_I: ['o_i'],
            Operator.S: ['s']})

    while instance.reuse_instance():
        t0 = instance.get_setting('t0', 'float')
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            t_cur = msg.timestamp
            i, t_stop = msg.data

        if instance.should_init():
            t_cur = t0
            i = 0
            t_stop = t0 + t_max

        rcvd_i = 0
        while t_cur < t_stop:
            # faux time-integration for testing snapshots
            t_next = t_cur + dt
            if t_next >= t_stop:
                t_next = None
            logging.info(f'Sending {i} at {t_cur}, next at {t_next}')
            instance.send('o_i', Message(t_cur, t_next, i))

            msg = instance.receive('s')
            logging.info(
                    f'Received {msg.data} from time {msg.timestamp},'
                    f' next at {msg.next_timestamp}')
            assert msg.data >= rcvd_i
            rcvd_i = msg.data

            t_cur += dt
            i += 1

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur, None, [i, t_stop]))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, None, [i, t_stop]))


def test_snapshot_interact_lockstep(tmp_path):
    config = f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    comp1: component
    comp2: component
  conduits:
    comp1.o_i: comp2.s
    comp2.o_i: comp1.s
settings:
  t0: 0.35
  dt: 0.1234
  t_max: 3.0
  muscle_remote_log_level: {_LOG_LEVEL}
checkpoints:
  simulation_time:
  - every: 1.0
    start: 0.75
    stop: 2.0
  - at:
    - 2.5"""
    actors = {f'comp{i + 1}': component for i in range(2)}

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(config, run_dir1.path, python_actors=actors)

    assert len(ls_snapshots(run_dir1, 'comp1')) == 3  # t=0.75, 1.75, 2.5
    assert len(ls_snapshots(run_dir1, 'comp2')) == 3  # t=0.75, 1.75, 2.5

    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 3

    # resume from the snapshots taken at t>=1.75
    run_dir2 = RunDir(tmp_path / 'run2')
    config_doc = load(config)
    config_doc.update(snapshot_docs[1])

    run_manager_with_actors(
            dump(config_doc), run_dir2.path, python_actors=actors)

    assert len(ls_snapshots(run_dir2, 'comp1')) == 2  # resume, t=2.5
    assert len(ls_snapshots(run_dir2, 'comp2')) == 2  # resume, t=2.5
    assert len(ls_snapshots(run_dir2)) == 2


@pytest.mark.parametrize('scale', [0.1, 0.9, 1.0, 1.1, 1.5])
def test_snapshot_interact_varstep(tmp_path, scale):
    config = f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    comp1: component
    comp2: component
    coupler: checkpointing_temporal_coupler
  conduits:
    comp1.o_i: coupler.a_in
    coupler.a_out: comp1.s
    comp2.o_i: coupler.b_in
    coupler.b_out: comp2.s
settings:
  t0: 0.35
  comp1.dt: 0.1234
  comp2.dt: {0.1234 * scale}
  t_max: 3.0
  muscle_remote_log_level: {_LOG_LEVEL}
checkpoints:
  simulation_time:
  - every: 1.0
    start: 0.75
    stop: 2.0
  - at:
    - 2.5"""
    actors = {f'comp{i + 1}': component for i in range(2)}
    actors['coupler'] = interact_coupling.checkpointing_temporal_coupler

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(config, run_dir1.path, python_actors=actors)

    assert len(ls_snapshots(run_dir1, 'comp1')) == 3  # t=0.75, 1.75, 2.5
    assert len(ls_snapshots(run_dir1, 'comp2')) == 3  # t=0.75, 1.75, 2.5

    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 3

    # resume from the snapshots taken at t>=1.75
    run_dir2 = RunDir(tmp_path / 'run2')
    config_doc = load(config)
    config_doc.update(snapshot_docs[1])

    run_manager_with_actors(
            dump(config_doc), run_dir2.path, python_actors=actors)

    assert len(ls_snapshots(run_dir2, 'comp1')) == 2  # resume, t=2.5
    assert len(ls_snapshots(run_dir2, 'comp2')) == 2  # resume, t=2.5
    assert len(ls_snapshots(run_dir2)) == 2
