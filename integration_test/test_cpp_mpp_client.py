import multiprocessing as mp
import os
from pathlib import Path
import subprocess
from unittest.mock import MagicMock

import msgpack

from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mpp_message import MPPMessage
from libmuscle.mcp.protocol import RequestType

from ymmsl import Reference, Settings

from .conftest import skip_if_python_only


def tcp_server_process(control_pipe):
    control_pipe[0].close()
    settings = Settings({'test_setting': 42})
    data = {'test1': 10, 'test2': [None, True, 'testing']}
    receiver = Reference('test_receiver.test_port2')
    message = MPPMessage(
            Reference('test_sender.test_port'),
            receiver,
            10, 1.0, 2.0, settings, 0, data).encoded()

    def handle_request(request_bytes):
        request = msgpack.unpackb(request_bytes, raw=False)
        assert request[0] == RequestType.GET_NEXT_MESSAGE.value
        assert request[1] == 'test_receiver.test_port2'
        return message

    post_office = MagicMock()
    post_office.done = False
    post_office.handle_request = handle_request

    server = TcpTransportServer(post_office)
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
    # see libmuscle/cpp/src/libmuscle/tests/mpp_client_test.cpp
    cpp_build_dir = Path(__file__).parents[1] / 'libmuscle' / 'cpp' / 'build'
    env = os.environ.copy()
    lib_paths = [cpp_build_dir / 'msgpack' / 'msgpack' / 'lib']
    if 'LD_LIBRARY_PATH' in env:
        env['LD_LIBRARY_PATH'] += ':' + ':'.join(map(str, lib_paths))
    else:
        env['LD_LIBRARY_PATH'] = ':'.join(map(str, lib_paths))

    cpp_test_dir = cpp_build_dir / 'libmuscle' / 'tests'
    cpp_test_client = cpp_test_dir / 'mpp_client_test'
    result = subprocess.run([str(cpp_test_client), server_loc], env=env)

    server_pipe[0].send(None)
    server_pipe[0].close()
    server_process.join()

    assert result.returncode == 0
    assert server_process.exitcode == 0
