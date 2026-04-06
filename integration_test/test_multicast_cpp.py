from ymmsl.v0_2 import Operator

from libmuscle import Instance

from .conftest import skip_if_python_only, run_manager_with_actors


def receiver():
    instance = Instance({Operator.F_INIT: ['in']})

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
ymmsl_version: v0.2
description: Testing multicast in C++
models:
- description: Multicast test model
  name: test_model
  components:
    multicast:
      ports:
        o_i: out
      description: Sending component that multicasts
      implementation: component
    receiver1:
      ports:
        f_init: in
      description: First receiver
      implementation: receiver
    receiver2:
      ports:
        f_init: in
      description: Second receiver
      implementation: receiver
  conduits:
    multicast.out:
    - receiver1.in
    - receiver2.in""",
        tmp_path,
        {'multicast': ('cpp', 'component_test'),
         'receiver1': ('python', receiver),
         'receiver2': ('python', receiver)})
