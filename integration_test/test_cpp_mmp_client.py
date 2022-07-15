import multiprocessing as mp
import os
from pathlib import Path
import subprocess

import ymmsl
from ymmsl import Operator, Port, Reference

from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir

from .conftest import skip_if_python_only


def do_mmp_client_test(tmpdir, caplog):
    ymmsl_text = (
            'ymmsl_version: v0.1\n'
            'model:\n'
            '  name: test_model\n'
            '  components:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n'
            'settings:\n'
            '  test1: 13\n'
            '  test2: 13.3\n'
            '  test3: testing\n'
            '  test4: True\n'
            '  test5: [2.3, 5.6]\n'
            '  test6:\n'
            '    - [1.0, 2.0]\n'
            '    - [3.0, 1.0]\n'
            )

    # create server
    ymmsl_doc = ymmsl.load(ymmsl_text)
    manager = Manager(ymmsl_doc, RunDir(Path(tmpdir)))

    # mock the deregistration
    removed_instance = None

    def mock_remove(name: Reference):
        nonlocal removed_instance
        removed_instance = name

    manager._instance_registry.remove = mock_remove

    # add some peers
    manager._instance_registry.add(
            Reference('macro'), ['tcp:test3', 'tcp:test4'],
            [Port('out', Operator.O_I), Port('in', Operator.S)])

    # create C++ client
    # it runs through the various RPC calls
    # see libmuscle/cpp/src/libmuscle/tests/mmp_client_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    env = os.environ.copy()
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] += ':' + ':'.join(map(str, lib_paths))
    else:
        env['LD_LIBRARY_PATH'] = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    cpp_test_client = cpp_test_dir / 'mmp_client_test'
    result = subprocess.run(
            [str(cpp_test_client), manager.get_server_location()], env=env)

    # check that C++-side checks were successful
    assert result.returncode == 0

    # check submit_log_message
    for rec in caplog.records:
        if rec.name == 'instances.test_logging':
            assert rec.time_stamp == '1970-01-01T00:00:02Z'
            assert rec.levelname == 'CRITICAL'
            assert rec.message == 'Integration testing'

    # check instance registry
    assert (manager._instance_registry.get_locations('micro[3]') ==
            ['tcp:test1', 'tcp:test2'])
    ports = manager._instance_registry.get_ports('micro[3]')
    assert ports[0].name == 'out'
    assert ports[0].operator == Operator.O_F
    assert ports[1].name == 'in'
    assert ports[1].operator == Operator.F_INIT

    # check deregister_instance
    assert removed_instance == 'micro[3]'

    manager.stop()


@skip_if_python_only
def test_mmp_client(log_file_in_tmpdir, tmpdir, caplog):
    process = mp.Process(target=do_mmp_client_test, args=(tmpdir, caplog))
    process.start()
    process.join()
    assert process.exitcode == 0
