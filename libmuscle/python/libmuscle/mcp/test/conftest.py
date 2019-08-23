import multiprocessing as mp

import pytest
from ymmsl import Reference

from libmuscle.mcp.direct_server import DirectServer
from libmuscle.mcp.tcp_server import TcpServer
from libmuscle.mcp.message import Message
from libmuscle.outbox import Outbox
from libmuscle.post_office import PostOffice


@pytest.fixture
def receiver():
    return Reference('test_receiver.test_port')


@pytest.fixture
def post_office(receiver):
    class MockPO(PostOffice):
        outboxes = {receiver: Outbox()}

        def get_message(self, receiver: Reference) -> Message:
            return self.outboxes[receiver].retrieve()

    return MockPO()


@pytest.fixture
def direct_server(post_office):
    return DirectServer('test_sender', post_office)


def tcp_server_process(connection, post_office, receiver):
    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), bytes())
    post_office.outboxes[receiver].deposit(message)
    server = TcpServer('test_sender', post_office)
    properties = dict()
    properties['instance_id'] = server._instance_id
    properties['location'] = server.get_location()
    connection.send(properties)
    connection.recv()
    connection.close()
    server.close()


@pytest.fixture
def tcp_server(post_office, receiver):
    pipe = mp.Pipe()
    proc = mp.Process(
            target=tcp_server_process,
            args=(pipe[1], post_office, receiver))
    proc.start()

    pipe[1].close()
    properties = pipe[0].recv()
    try:
        yield properties
    finally:
        pipe[0].send(None)
        pipe[0].close()
        proc.join()
        assert proc.exitcode == 0
