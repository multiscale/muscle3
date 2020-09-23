import multiprocessing as mp
from pathlib import Path
import subprocess
from unittest.mock import MagicMock

from libmuscle.mcp.tcp_server import TcpServer
from libmuscle.mcp.message import Message

from ymmsl import Reference, Settings

from .conftest import skip_if_python_only


def tcp_server_process(control_pipe):
    control_pipe[0].close()
    settings = Settings({'test_setting': 42})
    data = {'test1': 10, 'test2': [None, True, 'testing']}
    receiver = Reference('test_receiver.test_port2')
    message = Message(
            Reference('test_sender.test_port'),
            receiver,
            10, 1.0, 2.0, settings, data).encoded()

    def get_message(receiver):
        assert receiver == 'test_receiver.test_port2'
        return message

    post_office = MagicMock()
    post_office.done = False
    post_office.get_message = get_message

    sender_instance_id = Reference('test_sender')
    server = TcpServer(sender_instance_id, post_office)
    control_pipe[1].send(server.get_location())
    control_pipe[1].recv()
    control_pipe[1].close()
    server.close()


@skip_if_python_only
def test_cpp_tcp_client(log_file_in_tmpdir):
    # create server process
    server_pipe = mp.Pipe()
    server_process = mp.Process(target=tcp_server_process, args=(server_pipe,))
    server_process.start()
    server_pipe[1].close()
    server_loc = server_pipe[0].recv()

    # create C++ client
    # it receives and checks settings, and sends a log message
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
    cpp_test_client = cpp_test_dir / 'tcp_client_test'
    result = subprocess.run([str(cpp_test_client), server_loc], env=env)

    server_pipe[0].send(None)
    server_pipe[0].close()
    server_process.join()

    assert result.returncode == 0
    assert server_process.exitcode == 0
