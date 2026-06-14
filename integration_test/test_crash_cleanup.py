from pathlib import Path

import ymmsl

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


@skip_if_python_only
def test_crash_cleanup(tmpdir):
    tmppath = Path(str(tmpdir))

    # find our test component and its requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'
    crash_component = cpp_test_dir / 'crashing_component_test'

    # make config
    ymmsl_text = f"""
ymmsl_version: v0.2
description: A crash cleanup test model
models:
- name: test_model
  description: A macro-micro model that crashes
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: A crashing macro model
      implementation: crashing_component
    micro:
      ports:
        f_init: init
        o_f: result
      description: A non-crashing micro model
      implementation: component
  conduits:
    macro.out: micro.init
    micro.result: macro.in
programs:
  crashing_component:
    env:
      LD_LIBRARY_PATH: {ld_lib_path}
    executable: {crash_component}
  component:
    env:
      LD_LIBRARY_PATH: {ld_lib_path}
    executable: {test_component}
resources:
  test_model.macro:
    threads: 1
  test_model.micro:
    threads: 1
"""

    config = ymmsl.load(ymmsl_text)

    # set up
    run_dir = RunDir(tmppath / 'run')

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir, 'DEBUG')
    try:
        manager.start_instances()
    except:  # noqa
        manager.stop()
        raise
    success = manager.wait()

    # check that all did not go well
    assert not success
