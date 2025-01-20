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
    ymmsl_text = ((
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
            '    macro:\n'
            '      ports:\n'
            '        o_i: out\n'
            '        s: in\n'
            '      implementation: crashing_component\n'
            '    micro:\n'
            '      ports:\n'
            '        f_init: init\n'
            '        o_f: result\n'
            '      implementation: component\n'
            '  conduits:\n'
            '    macro.out: micro.init\n'
            '    micro.result: macro.in\n'
            'implementations:\n'
            '  crashing_component:\n'
            '    env:\n'
            '      LD_LIBRARY_PATH: {}\n'
            '    executable: {}\n'
            '  component:\n'
            '    env:\n'
            '      LD_LIBRARY_PATH: {}\n'
            '    executable: {}\n'
            'resources:\n'
            '  macro:\n'
            '    threads: 1\n'
            '  micro:\n'
            '    threads: 1\n'
            ).format(
                ld_lib_path, crash_component, ld_lib_path, test_component))

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
