from .conftest import run_manager_with_actors

import pytest
from ymmsl import ImplementationState, Operator, load, dump

from libmuscle import Instance, Message
from libmuscle.manager.run_dir import RunDir


_LOG_LEVEL = 'INFO'  # set to DEBUG for additional debug info


def macro():
    instance = Instance({
            Operator.O_I: ['o_i'],
            Operator.S: ['s']})

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
                instance.save_snapshot(Message(t_cur, None, i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, None, i))


def macro_vector():
    instance = Instance({
            Operator.O_I: ['o_i[]'],
            Operator.S: ['s[]']})

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
                instance.save_snapshot(Message(t_cur, None, i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, None, i))


def micro():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']})

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
                instance.save_snapshot(Message(t_cur, None, [i, t_stop]))

        instance.send('o_f', Message(t_cur, None, i))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, None, [i, t_stop]))


def stateless_micro():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']},
            stateful=ImplementationState.STATELESS)

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

        instance.send('o_f', Message(t_cur, None, i))


def data_transformer():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']},
            stateful=ImplementationState.STATELESS)

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
    actors = {'macro': macro, 'micro': micro}
    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(
            dump(base_config), run_dir1.path, python_actors=actors)

    # Note: sorted only works because we have fewer than 10 snapshots, otherwise
    # _10 would be sorted right after _1
    macro_snapshots = sorted(run_dir1.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    micro_snapshots = sorted(run_dir1.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir1.snapshot_dir().glob('snapshot_*.ymmsl'))
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
    run_manager_with_actors(
            dump(base_config), run_dir2.path, python_actors=actors)

    macro_snapshots = sorted(run_dir2.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 2  # 1.6, final
    micro_snapshots = sorted(run_dir2.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 2  # 1.6, final
    snapshots_ymmsl = sorted(run_dir2.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 2

    # resume from the first workflow snapshot (this restarts macro from scratch)
    run_dir3 = RunDir(tmp_path / 'run3')
    base_config.resume = {}                     # clear resume information
    base_config.update(snapshot_docs[0])        # add resume info
    base_config.settings['macro.t_max'] = 0.6   # run shorter
    run_manager_with_actors(
            dump(base_config), run_dir3.path, python_actors=actors)


def test_snapshot_macro_stateless_micro(tmp_path, base_config):
    actors = {'macro': macro, 'micro': stateless_micro}
    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(
            dump(base_config), run_dir1.path, python_actors=actors)

    # Note: sorted only works because we have fewer than 10 snapshots, otherwise
    # _10 would be sorted right after _1
    macro_snapshots = sorted(run_dir1.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    micro_snapshots = sorted(run_dir1.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir1.snapshot_dir().glob('snapshot_*.ymmsl'))
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 6

    # resume from the snapshot taken at t>=1.2
    run_dir2 = RunDir(tmp_path / 'run2')
    base_config.update(snapshot_docs[3])  # add resume info
    run_manager_with_actors(
            dump(base_config), run_dir2.path, python_actors=actors)

    macro_snapshots = sorted(run_dir2.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 2  # 1.6, final
    micro_snapshots = sorted(run_dir2.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 3  # 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir2.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 2


def test_snapshot_macro_vector_micro(tmp_path, base_config):
    base_config.model.components[1].multiplicity = [2]
    actors = {'macro': macro_vector, 'micro[0]': micro, 'micro[1]': micro}

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(
            dump(base_config), run_dir1.path, python_actors=actors)

    macro_snapshots = sorted(run_dir1.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    micro_snapshots = sorted(run_dir1.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 6 * 2  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir1.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 8

    run_dir2 = RunDir(tmp_path / 'run2')
    base_config.update(load(snapshots_ymmsl[-3]))  # add resume info
    run_manager_with_actors(
            dump(base_config), run_dir2.path, python_actors=actors)

    macro_snapshots = sorted(run_dir2.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 2  # 1.6, final
    micro_snapshots = sorted(run_dir2.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 2 * 2  # 1.6, final
    snapshots_ymmsl = sorted(run_dir2.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 2


def test_snapshot_macro_transformer_micro(tmp_path, config_with_transformer):
    actors = {'macro': macro, 'micro': micro, 'transformer1': data_transformer,
              'transformer2': data_transformer}

    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(
            dump(config_with_transformer), run_dir1.path, python_actors=actors)

    snapshots_ymmsl = sorted(run_dir1.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 8

    # pick one to resume from
    run_dir2 = RunDir(tmp_path / 'run2')
    config_with_transformer.update(load(snapshots_ymmsl[4]))  # add resume info
    run_manager_with_actors(
            dump(config_with_transformer), run_dir2.path, python_actors=actors)

    snapshots_ymmsl = sorted(run_dir2.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 3
