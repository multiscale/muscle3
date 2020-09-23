from ymmsl import Reference

from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.message import Message


def test_send_receive(receiver, direct_server, post_office):
    assert DirectClient.can_connect_to(direct_server.get_location())
    client = DirectClient(Reference('test_receiver'),
                          direct_server.get_location())

    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), 'message'.encode('utf-8'))

    post_office.outboxes[receiver].deposit(message)
    message2 = client.receive(receiver)

    assert message == message2
