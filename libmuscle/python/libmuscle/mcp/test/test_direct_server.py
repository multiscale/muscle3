from typing import Dict

import pytest
from ymmsl import Reference

from libmuscle.outbox import Outbox
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


def test_create(server):
    assert server._DirectServer__id in registered_servers
    assert registered_servers[server._DirectServer__id] == server


def test_location(server):
    assert server.get_location().startswith('direct:')


def test_request(receiver, outboxes, server):
    message = Message(Reference.from_string('test_sender.test_port'),
                      receiver, bytes())
    outboxes[receiver].deposit(message)
    assert server.request(receiver) == message
