import sys
import pytest
from ymmsl import Operator, load

from libmuscle import Instance, Message
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir


def macro():
    instance = Instance({
            Operator.O_I: ['o_i'],
            Operator.S: ['s']})

    while instance.reuse_instance():
        t_cur = instance.get_setting('t0', 'float')
        dt = instance.get_setting('dt', 'float')
        t_max = instance.get_setting('t_max', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            t_cur = msg.timestamp
            assert msg.next_timestamp == pytest.approx(t_cur + dt)
            i = msg.data
            assert i >= 0
        else:
            i = 0

        while t_cur + dt <= t_max:
            t_next = t_cur + dt

            if instance.should_save_snapshot(t_cur, t_next):
                instance.save_snapshot(Message(t_cur, t_next, i))

            t_next = None if t_next + dt > t_max else t_next
            instance.send('o_i', Message(t_cur, t_next, i))

            msg = instance.receive('s')
            assert msg.data == i

            i += 1
            t_cur += dt

        if instance.should_save_final_snapshot(t_cur):
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
        else:
            msg = instance.receive('f_i')
            t_cur = msg.timestamp
            i = msg.data
            t_stop = t_cur + t_max

        while t_cur < t_stop:
            t_next = t_cur + dt

            if instance.should_save_snapshot(t_cur, t_next):
                instance.save_snapshot(Message(t_cur, t_next, [i, t_stop]))

            t_cur += dt

        if instance.should_save_final_snapshot(t_cur):
            instance.save_final_snapshot(Message(t_cur, None, [i, t_stop]))

        instance.send('o_f', Message(t_cur, None, i))


def test_snapshot_macro_micro(tmp_path):
    ymmsl_text = f"""ymmsl_version: v0.1
model:
  name: test_snapshot
  components:
    macro: macro_implementation
    micro: micro_implementation
  conduits:
    macro.o_i: micro.f_i
    micro.o_f: macro.s
settings:
  macro.t0: 0.12
  macro.dt: 0.17
  macro.t_max: 1.9
  micro.dt: 0.009
  micro.t_max: 0.1
  muscle_remote_log_level: DEBUG
implementations:
  macro_implementation:
    executable: {sys.executable}
    args:
    - {__file__}
    - macro
    supports_checkpoint: true
  micro_implementation:
    executable: {sys.executable}
    args:
    - {__file__}
    - micro
    supports_checkpoint: true
resources:
  macro:
    threads: 1
  micro:
    threads: 1
checkpoints:
  simulation_time:
  - every: 0.4"""
    ymmsl_doc = load(ymmsl_text)

    run_dir1 = RunDir(tmp_path / 'run1')
    manager = Manager(ymmsl_doc, run_dir1)
    manager.start_instances()
    assert manager.wait()

    # Note: sorted only works because we have fewer than 10 snapshots, otherwise
    # _10 would be sorted right after _1
    macro_snapshots = sorted(run_dir1.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    micro_snapshots = sorted(run_dir1.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 6  # 0, 0.4, 0.8, 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir1.snapshot_dir().glob('snapshot_*.ymmsl'))
    snapshot_docs = list(map(load, snapshots_ymmsl))
    assert snapshot_docs[0].resume['macro'] == macro_snapshots[0]
    assert snapshot_docs[0].resume['micro'] == micro_snapshots[0]
    assert snapshot_docs[1].resume['macro'] == macro_snapshots[1]
    assert snapshot_docs[1].resume['micro'] == micro_snapshots[0]
    for i in range(2, 7):
        assert snapshot_docs[i].resume['macro'] == macro_snapshots[i - 1]
        assert snapshot_docs[i].resume['micro'] == micro_snapshots[i - 1]

    ymmsl_doc.update(snapshot_docs[4])
    del ymmsl_doc.settings['muscle_snapshot_directory']
    run_dir2 = RunDir(tmp_path / 'run2')
    manager = Manager(ymmsl_doc, run_dir2)
    manager.start_instances()
    assert manager.wait()

    macro_snapshots = sorted(run_dir2.snapshot_dir().glob('macro*'))
    assert len(macro_snapshots) == 2  # 1.6, final
    micro_snapshots = sorted(run_dir2.snapshot_dir().glob('micro*'))
    assert len(micro_snapshots) == 3  # 1.2, 1.6, final
    snapshots_ymmsl = sorted(run_dir2.snapshot_dir().glob('snapshot_*.ymmsl'))
    assert len(snapshots_ymmsl) == 2


if __name__ == "__main__":
    if 'macro' in sys.argv:
        macro()
    elif 'micro' in sys.argv:
        micro()
    else:
        raise RuntimeError('Specify macro or micro on the command line')
