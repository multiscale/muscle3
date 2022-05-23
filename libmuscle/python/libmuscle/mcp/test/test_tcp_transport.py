from unittest.mock import MagicMock

from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.mcp.tcp_transport_server import TcpTransportServer


def test_tcp_transport():
    request = b'request'
    response = b'response'

    def handle_request(request: bytes) -> bytes:
        assert request == b'request'
        return response

    handler = MagicMock()
    handler.handle_request = handle_request

    # create server
    server = TcpTransportServer(handler)

    # create client
    server_location = server.get_location()
    assert TcpTransportClient.can_connect_to(server_location)
    client = TcpTransportClient(server_location)

    response2 = client.call(request)
    assert response == response2

    client.close()
    server.close()
