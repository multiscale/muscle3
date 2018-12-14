from libmuscle.communicator import Communicator, Endpoint
from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.message import Message

from ymmsl import Conduit, Identifier, Reference

import msgpack
import pytest
from unittest.mock import patch, MagicMock


def test_endpoint() -> None:
    kernel = Reference('test.kernel')
    index = [42]
    port = Identifier('out')
    slot = [2]

    endpoint = Endpoint(kernel, index, port, slot)
    assert endpoint.kernel == kernel
    assert endpoint.index == index
    assert endpoint.port == port
    assert endpoint.slot == slot

    assert str(endpoint) == 'test.kernel[42].out[2]'


def test_endpoint_instance() -> None:
    endpoint = Endpoint(Reference('test.kernel'), [42], Identifier('port'),
                        [2])
    assert endpoint.instance() == 'test.kernel[42]'

    endpoint2 = Endpoint(Reference('test.kernel'), [], Identifier('port'), [])
    assert endpoint2.instance() == 'test.kernel'

    endpoint3 = Endpoint(Reference('test.kernel'), [], Identifier('port'), [3])
    assert endpoint3.instance() == 'test.kernel'


@pytest.fixture
def communicator() -> Communicator:
    instance_id = Reference('kernel[13]')
    communicator = Communicator(instance_id)
    communicator._Communicator__peers = {
            'kernel.out': Reference('other.in'),
            'kernel.in': Reference('other.out')
            }
    communicator._Communicator__peer_dims = {Reference('other'): []}
    communicator._Communicator__peer_locations = {
            Reference('other'): ['direct:test']}
    return communicator


@pytest.fixture
def communicator2() -> Communicator:
    instance_id = Reference('other')
    communicator = Communicator(instance_id)
    communicator._Communicator__peers = {
            'other.out': Reference('kernel.in'),
            'other.in': Reference('kernel.out')
            }
    communicator._Communicator__peer_dims = {Reference('kernel'): [20]}
    return communicator


def test_create_communicator(communicator) -> None:
    assert str(communicator._Communicator__kernel) == 'kernel'
    assert communicator._Communicator__index == [13]
    assert len(communicator._Communicator__servers) == 1
    assert communicator._Communicator__clients == {}
    assert communicator._Communicator__outboxes == {}


def test_get_locations(communicator) -> None:
    assert len(communicator.get_locations()) == 1
    assert communicator.get_locations()[0].startswith('direct:')


def test_connect(communicator) -> None:
    ref = Reference

    conduits = [Conduit(ref('kernel.out'), ref('other.in')),
                Conduit(ref('other.out'), ref('kernel.in'))]
    peer_dims = {ref('other'): [1]}
    peer_locations = {ref('other'): ['direct:test']}

    communicator.connect(conduits, peer_dims, peer_locations)

    assert (str(communicator._Communicator__peers['kernel.out']) ==
            'other.in')
    assert (str(communicator._Communicator__peers['kernel.in']) ==
            'other.out')

    assert communicator._Communicator__peer_dims == peer_dims
    assert communicator._Communicator__peer_locations == peer_locations


def test_send_message(communicator) -> None:
    ref = Reference
    communicator.send_message('out', 'test'.encode('utf-8'))

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.data.decode('utf-8') == 'test'


def test_send_on_invalid_port(communicator) -> None:
    with pytest.raises(ValueError):
        communicator.send_message('[$Invalid_id', 'test'.encode('utf-8'))

    with pytest.raises(ValueError):
        communicator.send_message('not_a_port', 'test'.encode('utf-8'))


def test_send_msgpack(communicator) -> None:
    ref = Reference
    communicator.send_message('out', {'test': 17})

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.data == msgpack.packb({'test': 17}, use_bin_type=True)


def test_send_message_with_slot(communicator2) -> None:
    ref = Reference
    communicator2.send_message('out', 'test'.encode('utf-8'), 13)

    assert 'kernel[13].in' in communicator2._Communicator__outboxes
    msg = communicator2._Communicator__outboxes[
            'kernel[13].in']._Outbox__queue[0]
    assert msg.sender == 'other.out[13]'
    assert msg.receiver == 'kernel[13].in'
    assert msg.data.decode('utf-8') == 'test'


def test_receive_message(communicator) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = Message(
            Reference('other.out[13]'), Reference('kernel[13].in'), b'test')
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in', False)

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('other.out[13]'))
    assert msg == b'test'


def test_receive_on_invalid_port(communicator) -> None:
    with pytest.raises(ValueError):
        communicator.receive_message('@$Invalid_id', b'test')
    with pytest.raises(ValueError):
        communicator.receive_message('does_not_exist', b'test')


def test_receive_msgpack(communicator) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = Message(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            msgpack.packb({'test': 13}))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in', True)

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('other.out[13]'))
    assert msg == {'test': 13}


def test_receive_with_slot(communicator2) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = Message(
            Reference('kernel[13].out'), Reference('other.in[13]'), b'test')
    get_client_mock = MagicMock(return_value=client_mock)
    communicator2._Communicator__get_client = get_client_mock

    msg = communicator2.receive_message('in', False, 13)

    get_client_mock.assert_called_with(Reference('kernel[13]'))
    client_mock.receive.assert_called_with(Reference('kernel[13].out'))
    assert msg == b'test'


@patch('libmuscle.mcp.direct_client.registered_servers')
def test_get_client(mock_servers, communicator) -> None:
    mock_servers.__contains__.return_value = True
    client = communicator._Communicator__get_client(Reference('other'))
    mock_servers.__contains__.assert_called_with('test')
    assert isinstance(client, DirectClient)

    client2 = communicator._Communicator__get_client(Reference('other'))
    assert client == client2

    communicator._Communicator__peer_locations[Reference('other2')] = [
            'non_existent:test']
    with pytest.raises(RuntimeError):
        communicator._Communicator__get_client(Reference('other2'))
