from pathlib import Path
import subprocess

from libmuscle.mcp.tcp_client import TcpClient
from libmuscle.mcp.message import Message

from ymmsl import Reference, Settings

from .conftest import skip_if_python_only


@skip_if_python_only
def test_cpp_tcp_server(log_file_in_tmpdir):
    # create C++ server
    # it serves a message for us to receive
    # see libmuscle/cpp/src/libmuscle/tests/mmp_server_test.cpp
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
    cpp_test_server = cpp_test_dir / 'tcp_server_test'
    server = subprocess.Popen(
            [str(cpp_test_server)], env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            universal_newlines=True, bufsize=1, close_fds=True)

    # get server location
    location = server.stdout.readline()

    assert TcpClient.can_connect_to(location)

    client = TcpClient(Reference('test_receiver'), location)
    msg = Message.from_bytes(client.receive(Reference('test_receiver.port')))
    client.close()

    # assert stuff
    assert msg.sender == 'test_sender.port'
    assert msg.receiver == 'test_receiver.port'
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.settings_overlay == Settings({'par1': 13})
    assert msg.data == {'var1': 1, 'var2': 2.0, 'var3': '3'}

    server.stdout.close()
    server.wait()
    assert server.returncode == 0
