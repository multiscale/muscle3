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
    ymmsl_text = ((
            'ymmsl_version: v0.2\n'
            'description: Nested version of the test_start_all model\n'
            'models:\n'
            '  test_model:\n'
            '    components:\n'
            '      macro:\n'
            '        ports:\n'
            '          o_i: out\n'
            '          s: in\n'
            '        description: The macro model\n'
            '        implementation: component\n'
            '      micro:\n'
            '        ports:\n'
            '          f_init: in\n'
            '          o_f: out\n'
            '        description: The micro model, wrapped in a submodel\n'
            '    conduits:\n'
            '      macro.out: micro.in\n'
            '      micro.out: macro.in\n'
            '  submodel:\n'
            '    ports:\n'
            '      f_init: in\n'
            '      o_f: out\n'
            '    components:\n'
            '      micro:\n'
            '        ports:\n'
            '          f_init: init\n'
            '          o_f: result\n'
            '        description: The micro model\n'
            '        implementation: component\n'
            '    conduits:\n'
            '      in: micro.init\n'
            '      micro.result: out\n'
            'custom_implementations:\n'
            '  micro.implementation: submodel\n'
            'programs:\n'
            '  component:\n'
            '    env:\n'
            '      +LD_LIBRARY_PATH: :{}\n'
            '    executable: {}\n'
            'resources:\n'
            '  test_model.macro:\n'
            '    threads: 1\n'
            '  test_model.micro.micro:\n'
            '    threads: 1\n'
            ).format(ld_lib_path, test_component))

    config = flatten(ymmsl.load(ymmsl_text))

    # set up
    run_dir = RunDir(tmppath / 'run')

    # launch MUSCLE Manager with simulation
    manager = Manager(config, run_dir, 'DEBUG')
    manager.start_instances()
    success = manager.wait()

    # check that all went well
    assert success
