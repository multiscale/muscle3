import pytest
from ymmsl import ImplementationState, Operator, load, dump

from libmuscle import Instance, Message
from libmuscle.manager.run_dir import RunDir

from .conftest import run_manager_with_actors, ls_snapshots


_LOG_LEVEL = 'INFO'  # set to DEBUG for additional debug info


def component():
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
            msg = instance.receive('f_i', default=Message(0, None, 0))
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


def stateless_component():
    instance = Instance({
            Operator.F_INIT: ['f_i'],
            Operator.O_F: ['o_f']},
            stateful=ImplementationState.STATELESS)

    while instance.reuse_instance():
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        msg = instance.receive('f_i', default=Message(0, None, 0))
        t_cur = msg.timestamp
        i = msg.data
        t_stop = t_cur + t_max

        while t_cur < t_stop:
            # faux time-integration for testing snapshots
            t_cur += dt

        instance.send('o_f', Message(t_cur, None, i))


@pytest.fixture
def dispatch_config():
    return load(f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    comp1: component
    comp2: component
    comp3: component
    comp4: component
    comp5: component
  conduits:
    comp1.o_f: comp2.f_i
    comp2.o_f: comp3.f_i
    comp3.o_f: comp4.f_i
    comp4.o_f: comp5.f_i
settings:
  dt: 0.1234
  t_max: 2.0
  muscle_remote_log_level: {_LOG_LEVEL}
checkpoints:
  at_end: true
  simulation_time:
  - every: 2.5
  - at:
    - 2.3
    - 2.8""")


def test_snapshot_dispatch(tmp_path, dispatch_config):
    actors = {f'comp{i + 1}': component for i in range(5)}
    (tmp_path / 'run1').mkdir()
    run_dir1 = RunDir(tmp_path / 'run1')
    run_manager_with_actors(
            dump(dispatch_config), run_dir1.path, python_actors=actors)

    assert len(ls_snapshots(run_dir1, 'comp1')) == 2  # t=0, at_end
    assert len(ls_snapshots(run_dir1, 'comp2')) == 5  # t=0, 2.5, 2.3, 2.8, at_end
    assert len(ls_snapshots(run_dir1, 'comp3')) == 3  # t=2.5, 5, at_end
    assert len(ls_snapshots(run_dir1, 'comp4')) == 3  # t=5, 7.5, at_end
    assert len(ls_snapshots(run_dir1, 'comp5')) == 3  # t=7.5, 10, at_end

    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert len(snapshot_docs) == 16

    # resume from the snapshots taken at t>=2.3
    (tmp_path / 'run2').mkdir()
    run_dir2 = RunDir(tmp_path / 'run2')
    dispatch_config.update(snapshot_docs[3])  # add resume info
    # validate resume info
    resume = snapshot_docs[3].resume
    assert resume['comp1'] == ls_snapshots(run_dir1, 'comp1')[1]
    assert resume['comp2'] == ls_snapshots(run_dir1, 'comp2')[1]
    assert 'comp3' not in resume
    assert 'comp4' not in resume
    assert 'comp5' not in resume

    run_manager_with_actors(
            dump(dispatch_config), run_dir2.path, python_actors=actors)

    assert len(ls_snapshots(run_dir2, 'comp1')) == 1  # resume
    assert len(ls_snapshots(run_dir2, 'comp2')) == 4  # resume, t=2.5, 2.8, at_end
    assert len(ls_snapshots(run_dir2, 'comp3')) == 3  # t=2.5, 5, at_end
    assert len(ls_snapshots(run_dir2, 'comp4')) == 3  # t=5, 7.5, at_end
    assert len(ls_snapshots(run_dir2, 'comp5')) == 3  # t=7.5, 10, at_end
    # More ymmsl restarts files may be possible, depending on the sequence of
    # incoming SnapshotMetadata...
    assert len(ls_snapshots(run_dir2)) >= 13
