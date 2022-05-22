import socket


def test_create(tcp_transport_server):
    assert tcp_transport_server._server_thread.is_alive()


def test_location(tcp_transport_server):
    assert tcp_transport_server.get_location().startswith('tcp:')


def test_request(tcp_transport_server):
    request = b'testing'
    response = b'response'

    tcp_transport_server._handler.handle_request.return_value = response

    location = tcp_transport_server._server.server_address
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.connect(location)
        length = len(request).to_bytes(8, byteorder='little')
        sock.sendall(length)
        sock.sendall(request)

        lenbuf = bytearray(8)
        sock.recv_into(lenbuf, 8)
        length = int.from_bytes(lenbuf, 'little')
        assert length == len(response)

        databuf = bytearray(length)
        received_count = 0
        while received_count < length:
            bytes_left = length - received_count
            received_count += sock.recv_into(
                    memoryview(databuf)[received_count:], bytes_left)

    assert databuf == response
