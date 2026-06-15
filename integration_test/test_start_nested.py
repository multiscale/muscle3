from pathlib import Path

import ymmsl
from libmuscle.manager.hammer import flatten
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


@skip_if_python_only
def test_start_nested(tmpdir):
    tmppath = Path(str(tmpdir))

    # find our test component and its requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'

    # make config
    ymmsl_text = f"""
ymmsl_version: v0.2
description: Nested version of the test_start_all model
models:
  test_model:
    components:
      macro:
        ports:
          o_i: out
          s: in
        description: The macro model
        implementation: component
      micro:
        ports:
          f_init: in
          o_f: out
        description: The micro model, wrapped in a submodel
    conduits:
      macro.out: micro.in
      micro.out: macro.in
  submodel:
    ports:
      f_init: in
      o_f: out
    components:
      micro:
        ports:
          f_init: init
          o_f: result
        description: The micro model
        implementation: component
    conduits:
      in: micro.init
      micro.result: out
custom_implementations:
  micro.implementation: submodel
programs:
  component:
    env:
      +LD_LIBRARY_PATH: :{ld_lib_path}
    executable: {test_component}
resources:
  test_model.macro:
    threads: 1
  test_model.micro.micro:
    threads: 1
"""

    config = flatten(ymmsl.load(ymmsl_text))

    # set up
    run_dir = RunDir(tmppath / 'run')

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir, 'DEBUG')
    manager.start_instances()
    success = manager.wait()

    # check that all went well
    assert success
