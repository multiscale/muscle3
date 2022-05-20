import os
from pathlib import Path

import pytest
import ymmsl

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


@skip_if_python_only
def test_start_script(tmpdir):
    # only run this if MPI is enabled
    if 'MUSCLE_ENABLE_MPI' not in os.environ:
        pytest.skip('MPI is not enabled, try with MUSCLE_ENABLE_MPI=1')

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
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
            '    macro:\n'
            '      ports:\n'
            '        o_i: out\n'
            '        s: in\n'
            '      implementation: component\n'
            '    micro:\n'
            '      ports:\n'
            '        f_init: init\n'
            '        o_f: result\n'
            '      implementation: mpi_component\n'
            '  conduits:\n'
            '    macro.out: micro.init\n'
            '    micro.result: macro.in\n'
            'implementations:\n'
            '  component: |\n'
            '    #!/bin/bash\n'
            '\n'
            '    export LD_LIBRARY_PATH={}\n'
            '\n'
            '    {}\n'
            '  mpi_component:\n'
            '    script:\n'
            '    - "#!/bin/bash"\n'
            '    - ""\n'
            '    - export LD_LIBRARY_PATH={}\n'
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
    manager = Manager(config, run_dir)
    manager.start_instances()
    success = manager.wait()

    # check that all went well
    assert success
