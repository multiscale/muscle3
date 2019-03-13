from libmuscle.mcp.direct_client import DirectClient
from ymmsl import Reference

from unittest.mock import patch


@patch('libmuscle.mcp.direct_client.registered_servers')
def test_can_connect_to(mock_servers) -> None:
    mock_servers.__contains__.return_value = True
    assert DirectClient.can_connect_to('direct:test_server')
    mock_servers.__contains__.assert_called_with('test_server')

    mock_servers.__contains__.return_value = False
    assert not DirectClient.can_connect_to('direct_test_server')


@patch('libmuscle.mcp.direct_client.registered_servers')
def test_create(mock_servers) -> None:
    mock_servers.__getitem__.return_value = 'mock_server'
    client = DirectClient(Reference('test_instance'), 'direct:test_server')
    assert client._DirectClient__server == 'mock_server'


@patch('libmuscle.mcp.direct_client.registered_servers')
def test_receive(mock_servers) -> None:
    client = DirectClient(Reference('test_instance'), 'direct:test_server')
    receiver = Reference('receiver')
    client.receive(receiver)
    client._DirectClient__server.request.assert_called_with(receiver)
