from unittest.mock import MagicMock

import pytest
from ymmsl import Reference

from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mpp_message import MPPMessage
from libmuscle.outbox import Outbox
from libmuscle.post_office import PostOffice


@pytest.fixture
def receiver():
    return Reference('test_receiver.test_port')


@pytest.fixture
def post_office(receiver):
    class MockPO(PostOffice):
        outboxes = {receiver: Outbox()}

        def get_message(self, receiver: Reference) -> MPPMessage:
            return self.outboxes[receiver].retrieve()

    return MockPO()


@pytest.fixture
def tcp_transport_server():
    server = TcpTransportServer(MagicMock())
    yield server
    server.close()
