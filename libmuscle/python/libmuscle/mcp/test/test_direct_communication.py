from unittest.mock import patch
from typing import Dict

import pytest
from ymmsl import Reference

from libmuscle.outbox import Outbox
from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.direct_server import DirectServer, registered_servers
from libmuscle.mcp.message import Message


@pytest.fixture
def receiver():
    return Reference.from_string('test_receiver.test_port')


@pytest.fixture
def outboxes(receiver):
    return {receiver: Outbox()}


@pytest.fixture
def server(outboxes):
    return DirectServer(outboxes)


def test_send_receive(receiver, server, outboxes):
    assert DirectClient.can_connect_to(server.get_location())
    client = DirectClient(server.get_location())

    message = Message(Reference.from_string('test_sender.test_port'),
                      receiver, 'message'.encode('utf-8'))

    outboxes[receiver].deposit(message)
    message2 = client.receive(receiver)

    assert message == message2
