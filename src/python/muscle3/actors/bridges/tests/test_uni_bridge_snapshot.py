import logging
import pickle
import random
from functools import partial
from pathlib import Path
from random import uniform
from textwrap import dedent

from integration_test.conftest import ls_snapshots
from ymmsl import dump, load_as
from ymmsl.v0_2 import Configuration, Operator
from ymmsl.v0_2 import Reference as Ref

from libmuscle import Instance, InstanceFlags, Message
from libmuscle.manager.run_dir import RunDir
from muscle3.actors.bridges.unidirectional_bridge import main as bridge
from muscle3.test.conftest import run_manager_with_actors


def simple_program() -> None:
    logger = logging.getLogger("program")
    instance = Instance(
        {Operator.O_I: ["data_out"], Operator.S: ["data_in"]},
        InstanceFlags.USES_CHECKPOINT_API,
    )

    while instance.reuse_instance():
        # f_init
        t_start = instance.get_setting("t_start", "float")
        t_end = instance.get_setting("t_end", "float")
        all_in_window = instance.get_setting("all_in_window", "bool")

        if instance.resuming():
            state_msg = instance.load_snapshot()
            t_cur = state_msg.timestamp
            random.setstate(pickle.loads(state_msg.data))

        if instance.should_init():
            t_cur = t_start

        while t_cur < t_end:
            # 0.6 to ensure dt is less than 5, so that there's at least one time point
            # between the starting point and the first checkpoint and we get a
            # consistent number of snapshots.
            t_next = t_cur + 10 ** uniform(-2.0, 0.6)
            logger.debug("t_cur = %s, t_next = %s", t_cur, t_next)

            # o_i
            t_next_sent = t_next if t_next < t_end else None
            instance.send("data_out", Message(t_cur, t_next_sent, t_cur))

            # s
            msg = instance.receive("data_in")
            logger.debug("Received data %s at %s", msg.data, msg.timestamp)

            if all_in_window:
                assert msg.timestamp == t_cur
                assert msg.next_timestamp == t_next_sent
                for ts, _ in msg.data:
                    assert t_cur <= ts
                    assert ts < t_next

            else:
                assert msg.timestamp < t_next

            t_cur = t_next

            if instance.should_save_snapshot(t_cur):
                rng_state = pickle.dumps(random.getstate())
                instance.save_snapshot(Message(t_cur, None, rng_state))

        if instance.should_save_final_snapshot():
            rng_state = pickle.dumps(random.getstate())
            instance.save_final_snapshot(Message(t_cur, None, rng_state))


_YMMSL_CONFIG = dedent("""
    ymmsl_version: v0.2

    imports:
    - from muscle3.actors.bridges import implementation unidirectional_bridge

    models:
      interact_varstep:
        description: |
          Two components with variable time stepping communication in both directions,
          using two unidirectional bridges.

        components:
          left:
            ports:
              o_i: data_out
              s: data_in
            description: One of the components
            implementation: simple_program

          right:
            ports:
              o_i: data_out
              s: data_in
            description: The other component
            implementation: simple_program

          ltr_bridge:
            ports:
              timeline sender:
                s: data_in
              timeline receiver:
                s: clock_in
                o_i: data_out
            description: Bridge that passes data from left to right
            implementation: unidirectional_bridge

          rtl_bridge:
            ports:
              timeline sender:
                s: data_in
              timeline receiver:
                s: clock_in
                o_i: data_out
            description: Bridge that passes data from right to left
            implementation: undirectional_bridge

        matching_timelines:
          left: ltr_bridge.sender rtl_bridge.receiver
          right: ltr_bridge.receiver rtl_bridge.sender

        conduits:
          rtl_bridge.data_out: left.data_in
          left.data_out:
            - rtl_bridge.clock_in
            - ltr_bridge.data_in

          ltr_bridge.data_out: right.data_in
          right.data_out:
            - ltr_bridge.clock_in
            - rtl_bridge.data_in

    settings:
      left.t_start: -25.0
      left.t_end: 25.0
      right.t_start: -15.0
      right.t_end: 35.0

      ltr_bridge.theta: 1.0
      ltr_bridge.strict_causality: true
      right.all_in_window: false

      rtl_bridge.all_in_window: true
      rtl_bridge.strict_causality: true
      left.all_in_window: true

    checkpoints:
      simulation_time:
        - every: 10
""")


# @pytest.mark.parametrize("scale", [0.1, 0.9, 1.0, 1.1, 1.5])
def test_uni_bridge_snapshot(tmp_path: Path) -> None:
    actors = {
        "left": ("python", simple_program),
        "right": ("python", simple_program),
        "ltr_bridge": ("python", bridge),
        "rtl_bridge": ("python", bridge),
    }

    run_dir1 = RunDir(tmp_path / "run1")
    run_manager_with_actors(_YMMSL_CONFIG, run_dir1.path, actors)

    assert len(ls_snapshots(run_dir1, Ref("left"))) == 6  # -30, -20, -10, 0, 10, 20
    assert len(ls_snapshots(run_dir1, Ref("right"))) == 6  # -10, 0, 10, 20, 30
    assert len(ls_snapshots(run_dir1, Ref("ltr_bridge"))) == 6
    assert len(ls_snapshots(run_dir1, Ref("rtl_bridge"))) == 6

    snapshots_ymmsl = ls_snapshots(run_dir1)
    snapshot_docs = list(map(partial(load_as, Configuration), snapshots_ymmsl))
    assert len(snapshot_docs) == 4  # -10, 0, 10, 20

    # resume from the snapshots taken at t=-10.0
    run_dir2 = RunDir(tmp_path / "run2")
    config_doc = load_as(Configuration, _YMMSL_CONFIG)
    config_doc.update(snapshot_docs[0])

    run_manager_with_actors(dump(config_doc), run_dir2.path, actors)

    assert len(ls_snapshots(run_dir2, Ref("left"))) == 4  # t=-10, 0, 10, 20
    assert (
        len(ls_snapshots(run_dir2, Ref("right"))) == 5
    )  # resume, t=-10, 0, 10, 20, 30
    assert len(ls_snapshots(run_dir2)) == 4
