import os
from pathlib import Path
import subprocess

from libmuscle.mpp_client import MPPClient
from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.mpp_message import MPPMessage

from ymmsl import Reference, Settings

from .conftest import skip_if_python_only


@skip_if_python_only
def test_cpp_tcp_server(log_file_in_tmpdir):
    # create C++ server
    # it serves a message for us to receive
    # see libmuscle/cpp/src/libmuscle/tests/mpp_server_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    env = os.environ.copy()
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] += ':' + ':'.join(map(str, lib_paths))
    else:
        env['LD_LIBRARY_PATH'] = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    cpp_test_server = cpp_test_dir / 'tcp_transport_server_test'
    server = subprocess.Popen(
            [str(cpp_test_server)], env=env, stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            universal_newlines=True, bufsize=1, close_fds=True)

    # get server location
    location = server.stdout.readline()

    assert TcpTransportClient.can_connect_to(location)

    client = MPPClient([location])
    msg = MPPMessage.from_bytes(client.receive(Reference('test_receiver.port')))
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
