from pathlib import Path

from ymmsl import load
from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation


def macro() -> None:
    """Macro model implementation."""
    instance = Instance({Operator.O_I: ["out"], Operator.S: ["in"]})

    while instance.reuse_instance():
        # o_i
        instance.send("out", Message(0.0, 10.0, "testing"))

        # s/b
        msg = instance.receive("in")
        assert msg.data == "testing"


def test_self_connection(log_file_in_tmpdir: None, tmp_path: Path) -> None:
    """Test connecting a component to itself."""
    model = """
ymmsl_version: v0.2
models:
  self_connection:
    components:
      macro:
        description: A macro model that talks to itself
        ports:
          o_i: out
          s: in
        implementation: macro_impl
    conduits:
      macro.out: macro.in
"""

    configuration = load(model)

    implementations = {"macro_impl": macro}
    run_simulation(configuration, implementations)
