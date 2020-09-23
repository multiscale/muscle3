from ymmsl import Reference

from libmuscle.mcp.tcp_client import TcpClient
from libmuscle.mcp.tcp_server import TcpServer


def test_send_receive(receiver, post_office):
    message = b'testing'

    # prepare post office
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
    assert message == message2

    client.close()
    TcpClient.shutdown(recv_instance_id)

    server.close()
