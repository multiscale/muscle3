import multiprocessing as mp
from pathlib import Path
import subprocess

import ymmsl
from ymmsl import Port, Reference

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.manager import elements_for_model
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.operator import Operator

from .conftest import skip_if_python_only


def do_mmp_client_test(caplog):
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
    logger = Logger()
    ymmsl_doc = ymmsl.load(ymmsl_text)
    expected_elements = elements_for_model(ymmsl_doc.model)
    instance_registry = InstanceRegistry(expected_elements)
    topology_store = TopologyStore(ymmsl_doc)
    server = MMPServer(logger, ymmsl_doc.settings, instance_registry,
                       topology_store)

    # mock the deregistration
    removed_instance = None

    def mock_remove(name: Reference):
        nonlocal removed_instance
        removed_instance = name

    instance_registry.remove = mock_remove

    # add some peers
    instance_registry.add(
            Reference('macro'), ['tcp:test3', 'tcp:test4'],
            [Port('out', Operator.O_I), Port('in', Operator.S)])

    # create C++ client
    # it runs through the various RPC calls
    # see libmuscle/cpp/src/libmuscle/tests/mmp_client_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    lib_paths = [
            cpp_build_dir / 'grpc' / 'c-ares' / 'c-ares' / 'lib',
            cpp_build_dir / 'grpc' / 'zlib' / 'zlib' / 'lib',
            cpp_build_dir / 'grpc' / 'openssl' / 'openssl' / 'lib',
            cpp_build_dir / 'protobuf' / 'protobuf' / 'lib',
            cpp_build_dir / 'grpc' / 'grpc' / 'lib',
            cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    env = {
            'LD_LIBRARY_PATH': ':'.join(map(str, lib_paths))}
    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    cpp_test_client = cpp_test_dir / 'mmp_client_test'
    result = subprocess.run([str(cpp_test_client)], env=env)

    # check that C++-side checks were successful
    assert result.returncode == 0

    # check submit_log_message
    for rec in caplog.records:
        if rec.name == 'instances.test_logging':
            assert rec.time_stamp == '1970-01-01T00:00:02Z'
            assert rec.levelname == 'CRITICAL'
            assert rec.message == 'Integration testing'
            break

    # check register_instance
    assert (instance_registry.get_locations('micro[3]') ==
            ['tcp:test1', 'tcp:test2'])
    ports = instance_registry.get_ports('micro[3]')
    assert ports[0].name == 'out'
    assert ports[0].operator == Operator.O_F
    assert ports[1].name == 'in'
    assert ports[1].operator == Operator.F_INIT

    # check deregister_instance
    assert removed_instance == 'micro[3]'

    server.stop()


@skip_if_python_only
def test_mmp_client(log_file_in_tmpdir, caplog):
    process = mp.Process(target=do_mmp_client_test, args=(caplog,))
    process.start()
    process.join()
    assert process.exitcode == 0
