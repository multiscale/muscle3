import socket

from ymmsl import Reference


def test_create(tcp_server):
    assert tcp_server._instance_id == Reference('test_sender')
    assert tcp_server._server_thread.is_alive()


def test_location(tcp_server):
    assert tcp_server.get_location().startswith('tcp:')


def test_request(receiver, post_office, tcp_server):
    message = b'testing'
    post_office.outboxes[receiver].deposit(message)

    location = tcp_server._server.server_address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(location)
        length = len(str(receiver)).to_bytes(8, byteorder='little')
        sock.sendall(length)
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

    assert databuf == message
