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
    ymmsl_text = ((
            'ymmsl_version: v0.2\n'
            'description: Configuration with a program with a start script\n'
            'models:\n'
            '- name: test_model\n'
            '  description: A macro micro model\n'
            '  components:\n'
            '    macro:\n'
            '      ports:\n'
            '        o_i: out\n'
            '        s: in\n'
            '      description: The macro model\n'
            '      implementation: program\n'
            '    micro:\n'
            '      ports:\n'
            '        f_init: init\n'
            '        o_f: result\n'
            '      description: The micro model, with a script implementation\n'
            '      implementation: mpi_program\n'
            '  conduits:\n'
            '    macro.out: micro.init\n'
            '    micro.result: macro.in\n'
            'programs:\n'
            '  program:\n'
            '    description: A program that is started with a script\n'
            '    script: |\n'
            '      #!/bin/bash\n'
            '\n'
            '      export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{}\n'
            '\n'
            '      {}\n'
            '  mpi_program:\n'
            '    description: An MPI program that is started with a script\n'
            '    script:\n'
            '    - "#!/bin/bash"\n'
            '    - ""\n'
            '    - export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:{}\n'
            '    - ""\n'
            '    - mpirun -n ${{MUSCLE_MPI_PROCESSES}} {}\n'
            'resources:\n'
            '  macro:\n'
            '    threads: 1\n'
            '  micro:\n'
            '    mpi_processes: 2\n'
            ).format(
                ld_lib_path, test_component, ld_lib_path, mpi_test_component))

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
