from pathlib import Path

import ymmsl

from libmuscle import Instance

from .conftest import skip_if_python_only, run_manager_with_actors


def receiver():
    instance = Instance({ymmsl.Operator.F_INIT: ['in']})

    i = 0
    while instance.reuse_instance():
        # f_init
        msg = instance.receive('in')
        assert msg.data == i
        assert isinstance(msg.data, int)
        i += 1


@skip_if_python_only
def test_multicast_cpp(tmp_path):
    run_manager_with_actors(
        """
ymmsl_version: v0.1
model:
  name: test_model
  components:
    multicast:
      implementation: component
    receiver1:
      implementation: receiver
    receiver2:
      implementation: receiver
  conduits:
    multicast.out:
    - receiver1.in
    - receiver2.in""",
        tmp_path,
        {'multicast': Path('libmuscle') / 'tests' / 'component_test'},
        {},
        {'receiver1': receiver, 'receiver2': receiver})
