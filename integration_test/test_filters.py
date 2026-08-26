import pytest
from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message

from .conftest import run_manager_with_actors, skip_if_python_only


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
