from pathlib import Path

import ymmsl

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


@skip_if_python_only
def test_base_env(tmpdir):
    tmppath = Path(str(tmpdir))

    # find our test component and its requirements
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    ld_lib_path = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    test_component = cpp_test_dir / 'component_test'

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
            '      implementation: component_clean\n'
            '    micro:\n'
            '      ports:\n'
            '        f_init: init\n'
            '        o_f: result\n'
            '      implementation: component_login\n'
            '  conduits:\n'
            '    macro.out: micro.init\n'
            '    micro.result: macro.in\n'
            'implementations:\n'
            '  component_clean:\n'
            '    base_env: clean\n'
            '    env:\n'
            '      +LD_LIBRARY_PATH: :{ld_lib_path}\n'
            '    executable: {test_component}\n'
            '  component_login:\n'
            '    base_env: login\n'
            '    env:\n'
            '      +LD_LIBRARY_PATH: :{ld_lib_path}\n'
            '    executable: {test_component}\n'
            'resources:\n'
            '  macro:\n'
            '    threads: 1\n'
            '  micro:\n'
            '    threads: 1\n'
            ).format(ld_lib_path=ld_lib_path, test_component=test_component))

    config = ymmsl.load(ymmsl_text)

    # set up
    run_dir = RunDir(tmppath / 'run')

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir, 'DEBUG')
    manager.start_instances()
    success = manager.wait()

    # check that all went well
    assert success
