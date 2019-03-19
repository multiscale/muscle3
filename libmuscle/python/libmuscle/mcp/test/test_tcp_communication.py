import time
from ymmsl import Reference

import pytest

from libmuscle.mcp.tcp_client import TcpClient
from libmuscle.mcp.tcp_server import TcpServer
from libmuscle.mcp.message import Message


def test_send_receive(receiver, post_office):
    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), 'message'.encode('utf-8'))

    # prepare post office, it's about to get forked
    post_office.outboxes[receiver].deposit(message)

    # create server
    sender_instance_id = Reference('test_sender')
    server = TcpServer(sender_instance_id, post_office)

    # create client
    recv_instance_id = Reference('test_receiver')

    server_location = server.get_location()
    assert TcpClient.can_connect_to(server_location)
    client = TcpClient(recv_instance_id, server_location)

    message2 = client.receive(receiver)
    assert message.sender == message2.sender
    assert message.receiver == message2.receiver
    assert message.port_length == message2.port_length
    assert message.timestamp == message2.timestamp
    assert message.next_timestamp == message2.next_timestamp
    assert message.parameter_overlay == message2.parameter_overlay
    assert message.data == message2.data

    client.close()
    TcpClient.shutdown(recv_instance_id)

    server.close()
