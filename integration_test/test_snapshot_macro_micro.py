import pytest
from ymmsl import Operator, load, dump

from libmuscle import (
        Instance, Message, KEEPS_NO_STATE_FOR_NEXT_USE, USES_CHECKPOINT_API)
from libmuscle.manager.run_dir import RunDir

from .conftest import run_manager_with_actors, ls_snapshots


_LOG_LEVEL = 'INFO'  # set to DEBUG for additional debug info


def macro():
    instance = Instance({
            Operator.O_I: ['o_i'],
            Operator.S: ['s']}, USES_CHECKPOINT_API)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            # load state from message
            t_cur = msg.timestamp
            i = msg.data
            assert i >= 1

        if instance.should_init():
            t_cur = instance.get_setting('t0', 'float')
            i = 0

        while t_cur + dt <= t_max:
            t_next = t_cur + dt
            if t_next + dt > t_max:
                t_next = None  # final iteration of this time-integration loop
            instance.send('o_i', Message(t_cur, t_next, i))

            msg = instance.receive('s')
            assert msg.data == i

            i += 1
            t_cur += dt

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur, data=i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, data=i))


def macro_vector():
    instance = Instance({
            Operator.O_I: ['o_i[]'],
            Operator.S: ['s[]']}, USES_CHECKPOINT_API)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            # load state from message
            t_cur = msg.timestamp
            i = msg.data
            assert i >= 1

        if instance.should_init():
            t_cur = instance.get_setting('t0', 'float')
            i = 0

        while t_cur + dt <= t_max:
            t_next = t_cur + dt
            if t_next + dt > t_max:
                t_next = None  # final iteration of this time-integration loop
            for slot in range(instance.get_port_length('o_i')):
                instance.send('o_i', Message(t_cur, t_next, i), slot)

            for slot in range(instance.get_port_length('s')):
                msg = instance.receive('s', slot)
                assert msg.data == i

            i += 1
            t_cur += dt

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur, data=i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, data=i))


def micro():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']}, USES_CHECKPOINT_API)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            t_cur = msg.timestamp
            i, t_stop = msg.data

        if instance.should_init():
            msg = instance.receive('f_i')
            t_cur = msg.timestamp
            i = msg.data
            t_stop = t_cur + t_max

        while t_cur < t_stop:
            # faux time-integration for testing snapshots
            t_cur += dt

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur, data=[i, t_stop]))

        instance.send('o_f', Message(t_cur, data=i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, data=[i, t_stop]))


def stateless_micro():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']},
            KEEPS_NO_STATE_FOR_NEXT_USE)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        msg = instance.receive('f_i')
        t_cur = msg.timestamp
        i = msg.data
        t_stop = t_cur + t_max

        while t_cur < t_stop:
            # faux time-integration for testing snapshots
            t_cur += dt

        instance.send('o_f', Message(t_cur, data=i))


def data_transformer():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']},
            KEEPS_NO_STATE_FOR_NEXT_USE)

    while instance.reuse_instance():
        msg = instance.receive('f_i')
        instance.send('o_f', msg)


@pytest.fixture
def base_config():
    return load(f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    macro: macro_implementation
    micro: micro_implementation
  conduits:
    macro.o_i: micro.f_i
    micro.o_f: macro.s
settings:
  macro.t0: 0.14
  macro.dt: 0.17
  macro.t_max: 1.9
  micro.dt: 0.009
  micro.t_max: 0.1
  muscle_remote_log_level: {_LOG_LEVEL}
checkpoints:
  at_end: true
  simulation_time:
  - every: 0.4""")


@pytest.fixture
def config_with_transformer(base_config):
    base_config.update(load("""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    transformer1: transformer
    transformer2: transformer
  conduits:
    macro.o_i: transformer1.f_i
    transformer1.o_f: micro.f_i
    micro.o_f: transformer2.f_i
    transformer2.o_f: macro.s"""))
    return base_config


def test_snapshot_macro_micro(tmp_path, base_config):
    actors = {'macro': ('python', macro), 'micro': ('python', micro)}
    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(dump(base_config), run_dir1.path, actors)

    macro_snapshots = ls_snapshots(run_dir1, 'macro')
    assert len(macro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    micro_snapshots = ls_snapshots(run_dir1, 'micro')
    assert len(micro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 7
    assert snapshot_docs[0].resume['macro'] == macro_snapshots[0]
    assert snapshot_docs[0].resume['micro'] == micro_snapshots[0]
    assert snapshot_docs[1].resume['macro'] == macro_snapshots[0]
    assert snapshot_docs[1].resume['micro'] == micro_snapshots[1]
    for i in range(2, 7):
        assert snapshot_docs[i].resume['macro'] == macro_snapshots[i - 1]
        assert snapshot_docs[i].resume['micro'] == micro_snapshots[i - 1]

    # resume from the snapshots taken at t>=1.2
    run_dir2 = RunDir(tmp_path / 'run2')
    base_config.update(snapshot_docs[4])  # add resume info
    run_manager_with_actors(dump(base_config), run_dir2.path, actors)

    assert len(ls_snapshots(run_dir2, 'macro')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2, 'micro')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2)) == 3

    # resume from the first workflow snapshot (this restarts macro from scratch)
    run_dir3 = RunDir(tmp_path / 'run3')
    base_config.resume = {}                     # clear resume information
    base_config.update(snapshot_docs[0])        # add resume info
    base_config.settings['macro.t_max'] = 0.6   # run shorter
    run_manager_with_actors(dump(base_config), run_dir3.path, actors)


def test_snapshot_macro_stateless_micro(tmp_path, base_config):
    actors = {'macro': ('python', macro), 'micro': ('python', stateless_micro)}
    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(dump(base_config), run_dir1.path, actors)

    assert len(ls_snapshots(run_dir1, 'macro')) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    assert len(ls_snapshots(run_dir1, 'micro')) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 6

    # resume from the snapshot taken at t>=1.2
    run_dir2 = RunDir(tmp_path / 'run2')
    base_config.update(snapshot_docs[3])  # add resume info
    run_manager_with_actors(dump(base_config), run_dir2.path, actors)

    assert len(ls_snapshots(run_dir2, 'macro')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2, 'micro')) == 4  # resume, 1.2, 1.6, final
    assert len(ls_snapshots(run_dir2)) == 3


def test_snapshot_macro_vector_micro(tmp_path, base_config):
    base_config.model.components[1].multiplicity = [2]
    actors = {'macro': ('python', macro_vector),
              'micro[0]': ('python', micro),
              'micro[1]': ('python', micro)}

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(dump(base_config), run_dir1.path, actors)

    assert len(ls_snapshots(run_dir1, 'macro')) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    assert len(ls_snapshots(run_dir1, 'micro[0]')) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    assert len(ls_snapshots(run_dir1, 'micro[1]')) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = ls_snapshots(run_dir1)
    assert len(snapshots_ymmsl) == 8

    run_dir2 = RunDir(tmp_path / 'run2')
    base_config.update(load(snapshots_ymmsl[-3]))  # add resume info
    run_manager_with_actors(dump(base_config), run_dir2.path, actors)

    assert len(ls_snapshots(run_dir2, 'macro')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2, 'micro[0]')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2, 'micro[1]')) == 3  # resume, 1.6, final
    assert len(ls_snapshots(run_dir2)) == 3


def test_snapshot_macro_transformer_micro(tmp_path, config_with_transformer):
    actors = {'macro': ('python', macro),
              'micro': ('python', micro),
              'transformer1': ('python', data_transformer),
              'transformer2': ('python', data_transformer)}

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(dump(config_with_transformer), run_dir1.path, actors)

    snapshots_ymmsl = ls_snapshots(run_dir1)
    assert len(snapshots_ymmsl) == 8

    # pick one to resume from
    run_dir2 = RunDir(tmp_path / 'run2')
    config_with_transformer.update(load(snapshots_ymmsl[4]))  # add resume info
    run_manager_with_actors(dump(config_with_transformer), run_dir2.path, actors)

    snapshots_ymmsl = ls_snapshots(run_dir2)
    assert len(snapshots_ymmsl) == 6
