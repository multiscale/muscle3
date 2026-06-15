import multiprocessing as mp
import os
import subprocess
from pathlib import Path

import ymmsl
from libmuscle.manager.manager import Manager
from libmuscle.manager.run_dir import RunDir
from libmuscle.timestamp import Timestamp
from ymmsl.v0_2 import Operator, Port, Reference

from .conftest import skip_if_python_only


def do_mmp_client_test(tmpdir, caplog):
    ymmsl_text = (
            'ymmsl_version: v0.2\n'
            'description: Configuration for testing MMP clients\n'
            'models:\n'
            '- name: test_model\n'
            '  description: A model for testing the MMP client\n'
            '  components:\n'
            '    macro:\n'
            '      description: Macro model\n'
            '      ports:\n'
            '        o_i: out\n'
            '        s: in\n'
            '      implementation: macro_implementation\n'
            '    micro:\n'
            '      description: Micro model\n'
            '      ports:\n'
            '        f_init: in\n'
            '        o_f: out\n'
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
    manager = Manager(ymmsl_doc, RunDir(Path(tmpdir)), 'DEBUG')

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

    # check submit_log_message (if supported, see below)
    if caplog is not None:
        for rec in caplog.records:
            if rec.name == 'test_logging':
                # N.B. string representation of iasctime depends on timezone settings
                assert rec.iasctime == Timestamp(2).to_asctime()
                assert rec.levelname == 'CRITICAL'
                assert rec.message == 'Integration testing'
                break
        else:
            raise RuntimeError(f"No log message for 'test_logging' in {caplog.records}")

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
    # caplog cannot be pickled, causing a crash if we try to pass it to the
    # process on platforms that don't fork. In this case, don't pass it and skip
    # the output check, if it works on one platform it'll work everywhere.
    pass_caplog = caplog if mp.get_start_method() != 'spawn' else None

    if mp.get_start_method() == "forkserver":
        # Python 3.14+ defaults to the forkserver start method, but we want to
        # run this test with the "fork" startmethod to test with caplog
        Process = mp.get_context("fork").Process
    else:
        Process = mp.Process

    process = Process(target=do_mmp_client_test, args=(tmpdir, pass_caplog))
    process.start()
    process.join()
    assert process.exitcode == 0
