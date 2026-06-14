from pathlib import Path

import ymmsl

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only, skip_if_no_mpi_cpp


@skip_if_python_only
@skip_if_no_mpi_cpp
def test_start_script(tmpdir):
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
description: Configuration with a program with a start script
models:
- name: test_model
  description: A macro micro model
  components:
    macro:
      ports:
        o_i: out
        s: in
      description: The macro model
      implementation: program
    micro:
      ports:
        f_init: init
        o_f: result
      description: The micro model, with a script implementation
      implementation: mpi_program
  conduits:
    macro.out: micro.init
    micro.result: macro.in
programs:
  program:
    description: A program that is started with a script
    script: |
      #!/bin/bash

      export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{ld_lib_path}

      {test_component}
  mpi_program:
    description: An MPI program that is started with a script
    script:
    - "#!/bin/bash"
    - ""
    - export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{ld_lib_path}
    - ""
    - mpirun -n ${{MUSCLE_MPI_PROCESSES}} {mpi_test_component}
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
