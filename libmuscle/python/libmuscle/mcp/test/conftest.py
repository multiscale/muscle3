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


@pytest.fixture
def tcp_server(post_office):
    server = TcpServer('test_sender', post_office)
    yield server
    server.close()
