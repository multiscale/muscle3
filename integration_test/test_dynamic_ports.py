from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message

from .conftest import run_manager_with_actors, skip_if_python_only

YMMSL = """\
ymmsl_version: v0.2

models:
  dynamic_model:
    components:
      macro:
        description: Dynamic macro
        ports:
          f_init: f_init
          o_i: o_i out2
          s: s
          o_f: o_f
      micro:
        description: Dynamic micro
        ports:
          f_init: init
          o_f: final
    conduits:
      macro.o_i: micro.init
      micro.final: macro.s
"""


def dynamic_macro():
    instance = Instance()

    while instance.reuse_instance():
        ports = instance.list_ports()

        assert ports[Operator.F_INIT] == ["f_init"]
        assert ports[Operator.O_I] == ["o_i", "out2"]
        assert ports[Operator.S] == ["s"]
        assert ports[Operator.O_F] == ["o_f"]

        assert not instance.is_connected("f_init")
        assert instance.is_connected("o_i")
        assert not instance.is_connected("out2")
        assert instance.is_connected("s")
        assert not instance.is_connected("o_f")

        # Send a message so that we're sure that dynamic_micro runs
        instance.send("o_i", Message(0.0))
        instance.receive("s")


def dynamic_micro():
    instance = Instance()

    while instance.reuse_instance():
        ports = instance.list_ports()

        assert ports == {Operator.F_INIT: ["init"], Operator.O_F: ["final"]}

        msg = instance.receive("init")
        instance.send("final", msg)


def test_dynamic_ports(tmp_path) -> None:
    run_manager_with_actors(
        YMMSL,
        tmp_path,
        {
            "macro": ("python", dynamic_macro),
            "micro": ("python", dynamic_micro),
        },
    )


@skip_if_python_only
def test_dynamic_ports_cpp(tmp_path) -> None:
    run_manager_with_actors(
        YMMSL,
        tmp_path,
        {
            "macro": ("cpp", "dynamic_macro_test"),
            "micro": ("python", dynamic_micro),
        },
    )
