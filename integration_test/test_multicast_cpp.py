from pathlib import Path
import sys

import ymmsl

from libmuscle import Instance
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

# when executing this file as a component, .conftest cannot be resolved
if __name__ == "__main__":
    def skip_if_python_only(func):
        return func
else:
    from .conftest import skip_if_python_only


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
def test_multicast_cpp(tmpdir):
    tmppath = Path(str(tmpdir))

    # find our test component and its requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'

    # make config
    ymmsl_text = f"""
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
    - receiver2.in
implementations:
  component:
    env:
      LD_LIBRARY_PATH: {ld_lib_path}
    executable: {test_component}
  receiver:
    executable: {sys.executable}
    args:
    - {__file__}
resources:
  multicast:
    threads: 1
  receiver1:
    threads: 1
  receiver2:
    threads: 1"""

    config = ymmsl.load(ymmsl_text)
    config.as_configuration().check_consistent()

    # set up
    run_dir = RunDir(tmppath / 'run')

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir)
    manager.start_instances()
    success = manager.wait()

    # check that all did not go well
    assert success


if __name__ == "__main__":
    receiver()
