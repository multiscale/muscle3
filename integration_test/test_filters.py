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
            instance.send("out", Message(i, data=msg.data + ["meso", i]))
        reused += 1


def micro() -> None:
    instance = Instance({Operator.F_INIT: ["in"], Operator.O_I: ["out"]})

    while instance.reuse_instance():
        msg = instance.receive("in")
        for i in range(2):
            instance.send("out", Message(i, data=msg.data + ["micro", i]))


def pico(filters: str) -> None:
    print("Running with conduit filter:", filters)
    instance = Instance({Operator.F_INIT: ["macro", "meso", "micro"]})

    reused = 0
    expected_counts = [
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
    while instance.reuse_instance():
        macro = instance.receive("macro")
        meso = instance.receive("meso")
        micro = instance.receive("micro")

        print("Received:", macro.data, meso.data, micro.data)
        message_counts = micro.data[1::2]
        assert message_counts == expected_counts[reused]

        # Test if macro message is padded or repeated, based on conduit filter filters
        if filters == "pad pad" and any(message_counts[1:]):
            assert macro.data is None
        elif filters == "repeat pad" and message_counts[-1]:
            assert macro.data is None
        else:
            assert macro.data == micro.data[:2]

        assert micro.data[:4] == meso.data

        assert micro.data[1::2] == expected_counts[reused]
        reused += 1

    assert reused == len(expected_counts)


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
      pico:
        description: pico
        ports:
          f_init: macro meso micro
        implementation: pico
    conduits:
      macro.out:
      - meso.in
      - {filters} pico.macro
      meso.out:
      - micro.in
      - repeat pico.meso
      micro.out: pico.micro
"""


@pytest.mark.parametrize("filters", ["repeat repeat", "repeat pad", "pad pad"])
def test_repeater_filters(tmp_path, filters):
    actors = {
        "macro": ("python", macro),
        "meso": ("python", meso),
        "micro": ("python", micro),
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
        "pico": ("cpp", "conduit_filters_test", filters),
    }
    run_manager_with_actors(config.format(filters=filters), tmp_path, actors)
