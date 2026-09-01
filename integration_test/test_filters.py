import pytest
from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message
from libmuscle.instance import InstanceFlags
from libmuscle.manager.run_dir import RunDir

from .conftest import ls_snapshots, run_manager_with_actors, skip_if_python_only


def macro() -> None:
    instance = Instance({Operator.O_I: ["out"]})

    while instance.reuse_instance():
        for i in range(4):
            instance.send("out", Message(i, data=["macro", i]))


def meso() -> None:
    instance = Instance({Operator.F_INIT: ["in"], Operator.O_I: ["out"]})

    reused = 0
    while instance.reuse_instance():
        msg = instance.receive("in")
        for i in range(reused):
            t = msg.timestamp + i / 10
            instance.send("out", Message(t, data=msg.data + ["meso", i]))
        reused += 1


def micro() -> None:
    instance = Instance({Operator.F_INIT: ["in"], Operator.O_I: ["out"]})

    while instance.reuse_instance():
        msg = instance.receive("in")
        for i in range(2):
            t = msg.timestamp + i / 100
            instance.send("out", Message(t, data=msg.data + ["micro", i]))


EXPECTED_COUNTS = [
    [1, 0, 0],
    [1, 0, 1],
    [2, 0, 0],
    [2, 0, 1],
    [2, 1, 0],
    [2, 1, 1],
    [3, 0, 0],
    [3, 0, 1],
    [3, 1, 0],
    [3, 1, 1],
    [3, 2, 0],
    [3, 2, 1],
]


def pico(filters: str) -> None:
    print("Running with conduit filter:", filters)
    instance = Instance({Operator.F_INIT: ["macro", "meso", "micro"]})

    reused = 0
    while instance.reuse_instance():
        macro = instance.receive("macro")
        meso = instance.receive("meso")
        micro = instance.receive("micro")

        print("Received:", macro.data, meso.data, micro.data)
        message_counts = micro.data[1::2]
        assert message_counts == EXPECTED_COUNTS[reused]

        # Test if macro message is padded or repeated, based on conduit filter filters
        if filters == "pad pad" and any(message_counts[1:]):
            assert macro.data is None
        elif filters == "repeat pad" and message_counts[-1]:
            assert macro.data is None
        else:
            assert macro.data == micro.data[:2]

        assert micro.data[:4] == meso.data
        reused += 1

    assert reused == len(EXPECTED_COUNTS)


def repeat_s(filters: str) -> None:
    instance = Instance(
        {Operator.F_INIT: ["meso"], Operator.S: ["macro", "repeated_meso", "micro"]}
    )

    micro_received = 0
    while instance.reuse_instance():
        meso = instance.receive("meso")
        print("Receveid meso:", meso.data)

        for _ in range(2):
            macro = instance.receive("macro")
            repeated_meso = instance.receive("repeated_meso")
            micro = instance.receive("micro")

            print("Received S:", macro.data, repeated_meso.data, micro.data)
            message_counts = micro.data[1::2]
            assert message_counts == EXPECTED_COUNTS[micro_received]

            # Test if macro message is padded or repeated
            if filters == "pad pad" and any(message_counts[1:]):
                assert macro.data is None
            elif filters == "repeat pad" and message_counts[-1]:
                assert macro.data is None
            else:
                assert macro.data == micro.data[:2]

            assert repeated_meso.data == meso.data
            assert micro.data[:4] == meso.data
            micro_received += 1
    assert micro_received == len(EXPECTED_COUNTS)


config = """
ymmsl_version: v0.2
models:
  repeaters:
    components:
      macro:
        description: macro
        ports:
          o_i: out
        implementation: macro
      meso:
        description: meso
        ports:
          f_init: in
          o_i: out
        implementation: meso
      micro:
        description: micro
        ports:
          f_init: in
          o_i: out
        implementation: micro
      repeat_s:
        description: micro with repeaters on S ports
        ports:
          f_init: meso
          timeline micro:
            s: macro repeated_meso micro
        implementation: repeat_s
      pico:
        description: pico
        ports:
          f_init: macro meso micro
        implementation: pico
    conduits:
      macro.out:
      - meso.in
      - {filters} pico.macro
      - {filters} repeat_s.macro
      meso.out:
      - micro.in
      - repeat pico.meso
      - repeat_s.meso
      - repeat repeat_s.repeated_meso
      micro.out:
      - pico.micro
      - repeat_s.micro
"""


@pytest.mark.parametrize("filters", ["repeat repeat", "repeat pad", "pad pad"])
def test_repeater_filters(tmp_path, filters):
    actors = {
        "macro": ("python", macro),
        "meso": ("python", meso),
        "micro": ("python", micro),
        "repeat_s": ("python", repeat_s, filters),
        "pico": ("python", pico, filters),
    }
    run_manager_with_actors(config.format(filters=filters), tmp_path, actors)


@skip_if_python_only
@pytest.mark.parametrize("filters", ["repeat repeat", "repeat pad", "pad pad"])
def test_repeater_filters_cpp(tmp_path, filters):
    actors = {
        "macro": ("python", macro),
        "meso": ("python", meso),
        "micro": ("python", micro),
        "repeat_s": ("cpp", "conduit_filters_test", "repeat_s", filters),
        "pico": ("cpp", "conduit_filters_test", "pico", filters),
    }
    run_manager_with_actors(config.format(filters=filters), tmp_path, actors)


checkpoint_config = """
ymmsl_version: v0.2
models:
  checkpointing:
    components:
      A:
        description: first component
        ports:
          o_f: out
        implementation: A
      B:
        description: second component
        ports:
          s: in
        implementation: B
    conduits:
      A.out: repeat B.in
checkpoints:
  at_end: true
  simulation_time:
  - at: 2
"""


def checkpointing_A():
    instance = Instance(
        {Operator.O_F: ["out"]},
        InstanceFlags.KEEPS_NO_STATE_FOR_NEXT_USE,
    )

    while instance.reuse_instance():
        instance.send("out", Message(5, data="xyz"))


def checkpointing_B():
    instance = Instance(
        {Operator.S: ["in"]},
        InstanceFlags.USES_CHECKPOINT_API,
    )

    while instance.reuse_instance():
        if instance.resuming():
            t_cur = instance.load_snapshot().timestamp
        if instance.should_init():
            t_cur = 0.0

        while t_cur < 5:
            msg = instance.receive("in")
            assert msg.data == "xyz"
            assert msg.timestamp == 5
            print("Message is alright!")

            t_cur += 1
            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur))


def test_repeater_filters_checkpoint(tmp_path):
    actors = {
        "A": ("python", checkpointing_A),
        "B": ("python", checkpointing_B),
    }
    run_checkpointing_config_with_actors(actors, tmp_path)


@skip_if_python_only
def test_repeater_filters_checkpoint_cpp(tmp_path):
    actors = {
        "A": ("cpp", "conduit_filters_test", "checkpointing_A"),
        "B": ("cpp", "conduit_filters_test", "checkpointing_B"),
    }
    run_checkpointing_config_with_actors(actors, tmp_path)


def run_checkpointing_config_with_actors(actors, tmp_path):
    run_dir1 = RunDir(tmp_path / "run1")
    run_manager_with_actors(checkpoint_config, run_dir1.path, actors)

    assert len(ls_snapshots(run_dir1, "A")) == 1  # at_end
    assert len(ls_snapshots(run_dir1, "B")) == 2  # t=2, at_end
    snapshots_ymmsl = ls_snapshots(run_dir1)
    assert len(snapshots_ymmsl) == 2

    # resume from the snapshot
    run_dir2 = RunDir(tmp_path / "run2")
    snapshot_txt = snapshots_ymmsl[0].read_text()

    run_manager_with_actors(
        checkpoint_config + snapshot_txt.removeprefix("ymmsl_version: v0.2"),
        run_dir2.path,
        actors,
    )
