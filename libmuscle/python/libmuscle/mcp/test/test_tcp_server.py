import socket
from typing import Dict

import msgpack
import pytest
from ymmsl import Reference

from libmuscle.outbox import Outbox
from libmuscle.post_office import PostOffice
from libmuscle.mcp.message import Message


def test_create(tcp_server):
    assert tcp_server._instance_id == Reference('test_sender')
    assert tcp_server._server_thread.is_alive()


def test_location(tcp_server):
    assert tcp_server.get_location().startswith('tcp:')


def test_request(receiver, post_office, tcp_server):
    message = Message(Reference('test_sender.test_port'), receiver,
                      None, 0.0, 1.0, bytes(), bytes())
    post_office.outboxes[receiver].deposit(message)

    location = tcp_server._server.server_address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(location)
        sock.sendall(str(receiver).encode('utf-8'))

        lenbuf = bytearray(8)
        sock.recv_into(lenbuf, 8)
        length = int.from_bytes(lenbuf, 'little')

        databuf = bytearray(length)
        received_count = 0
        while received_count < length:
            bytes_left = length - received_count
            received_count += sock.recv_into(
                    memoryview(databuf)[received_count:], bytes_left)

    message_dict = msgpack.unpackb(databuf, raw=False)
    assert message_dict['sender'] == 'test_sender.test_port'
    assert message_dict['receiver'] == str(receiver)
    assert message_dict['port_length'] is None
    assert message_dict['timestamp'] == 0.0
    assert message_dict['next_timestamp'] == 1.0
    assert message_dict['parameter_overlay'] == bytes()
    assert message_dict['data'] == bytes()
