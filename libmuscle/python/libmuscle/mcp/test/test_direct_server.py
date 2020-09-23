from ymmsl import Reference

from libmuscle.mcp.direct_server import registered_servers
from libmuscle.mcp.message import Message


def test_create(direct_server):
    assert direct_server._DirectServer__id in registered_servers
    assert registered_servers[direct_server._DirectServer__id] == direct_server


def test_location(direct_server):
    assert direct_server.get_location().startswith('direct:')


def test_request(receiver, post_office, direct_server):
    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), bytes())
    post_office.outboxes[receiver].deposit(message)
    assert direct_server.request(receiver) == message
