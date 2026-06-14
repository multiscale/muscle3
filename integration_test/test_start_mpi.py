from pathlib import Path

import ymmsl

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only, skip_if_no_mpi_cpp


@skip_if_python_only
@skip_if_no_mpi_cpp
def test_start_mpi(tmpdir, mpi_exec_model):
    tmppath = Path(str(tmpdir))

    # find our test components and their requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'
    mpi_test_component = cpp_test_dir / 'mpi_component_test'

    # make config
    ymmsl_text = f"""
ymmsl_version: v0.2
description: Configuration to test starting models with MPI
models:
- name: test_model
  description: Macro-micro model with an MPI implementation
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: The macro model
      implementation: component
    micro:
      ports:
        f_init: init
        o_f: result
      description: The micro model, parallel version
      implementation: mpi_component
  conduits:
    macro.out: micro.init
    micro.result: macro.in
programs:
  component:
    env:
      +LD_LIBRARY_PATH: :{ld_lib_path}
    executable: {test_component}
  mpi_component:
    env:
      +LD_LIBRARY_PATH: :{ld_lib_path}
    executable: {mpi_test_component}
    execution_model: {mpi_exec_model}
resources:
  test_model.macro:
    threads: 1
  test_model.micro:
    mpi_processes: 2
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

    # check that all went well
    assert success
