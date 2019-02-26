from libmuscle.communicator import Communicator, Endpoint, Message
from libmuscle.configuration import Configuration
from libmuscle.mcp.direct_client import DirectClient
from libmuscle.mcp.message import Message as MCPMessage

from ymmsl import Conduit, Identifier, Operator, Reference

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
    instance_id = Reference('kernel')
    communicator = Communicator(instance_id, [13])
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
    communicator = Communicator(instance_id, [])
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


def test_send_message(communicator, message) -> None:
    ref = Reference
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.timestamp == 0.0
    assert msg.next_timestamp is None
    assert msg.parameter_overlay == msgpack.packb({}, use_bin_type=True)
    assert msg.data == msgpack.packb(b'test', use_bin_type=True)


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


def test_send_on_disconnected_port(communicator, message) -> None:
    communicator.send_message('not_connected', message)


def test_send_on_invalid_port(communicator, message) -> None:
    with pytest.raises(ValueError):
        communicator.send_message('[$Invalid_id', message)


def test_send_msgpack(communicator, message2) -> None:
    ref = Reference
    communicator.send_message('out', message2)

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.parameter_overlay == msgpack.packb({}, use_bin_type=True)
    assert msg.data == msgpack.packb({'test': 17}, use_bin_type=True)


def test_send_message_with_slot(communicator2, message) -> None:
    ref = Reference
    communicator2.send_message('out', message, 13)

    assert 'kernel[13].in' in communicator2._Communicator__outboxes
    msg = communicator2._Communicator__outboxes[
            'kernel[13].in']._Outbox__queue[0]
    assert msg.sender == 'other.out[13]'
    assert msg.receiver == 'kernel[13].in'
    assert msg.parameter_overlay == msgpack.packb({}, use_bin_type=True)
    assert msgpack.unpackb(msg.data).decode('utf-8') == 'test'


def test_send_message_with_parameters(communicator, message) -> None:
    ref = Reference
    message.configuration['test2'] = 'testing'
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msgpack.unpackb(msg.parameter_overlay, raw=False) == {
            'test2': 'testing'}
    assert msgpack.unpackb(msg.data).decode('utf-8') == 'test'


def test_send_configuration(communicator, message) -> None:
    ref = Reference
    message.data = Configuration()
    message.data['test1'] = 'testing'
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.parameter_overlay == msgpack.packb({})
    assert msg.data == msgpack.packb(
            msgpack.ExtType(1, msgpack.packb({'test1': 'testing'},
                                             use_bin_type=True)),
            use_bin_type=True)


def test_receive_message(communicator) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MCPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            0.0, None, msgpack.packb({'test1': 12}),
            msgpack.packb(b'test', use_bin_type=True))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == b'test'
    assert msg.configuration['test1'] == 12


def test_receive_message_default(communicator) -> None:
    default_msg = Message(3.0, 4.0, 'test', Configuration())
    msg = communicator.receive_message('not_connected', default=default_msg)
    assert msg.timestamp == 3.0
    assert msg.next_timestamp == 4.0
    assert msg.data == 'test'
    assert len(msg.configuration) == 0


def test_receive_message_no_default(communicator) -> None:
    with pytest.raises(RuntimeError):
        communicator.receive_message('not_connected')


def test_receive_on_invalid_port(communicator) -> None:
    with pytest.raises(ValueError):
        communicator.receive_message('@$Invalid_id')


def test_receive_msgpack(communicator) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MCPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            0.0, None, msgpack.packb({'test1': 12}),
            msgpack.packb({'test': 13}))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == {'test': 13}


def test_receive_with_slot(communicator2) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MCPMessage(
            Reference('kernel[13].out'), Reference('other.in[13]'),
            0.0, None, msgpack.packb({'test': 'testing'}),
            msgpack.packb(b'test', use_bin_type=True))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator2._Communicator__get_client = get_client_mock

    msg = communicator2.receive_message('in', 13)

    get_client_mock.assert_called_with(Reference('kernel[13]'))
    client_mock.receive.assert_called_with(Reference('other.in[13]'))
    assert msg.data == b'test'
    assert msg.configuration['test'] == 'testing'


def test_receive_with_parameters(communicator) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MCPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            0.0, None, msgpack.packb({'test2': 3.1}),
            msgpack.packb(b'test', use_bin_type=True))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == b'test'
    assert msg.configuration['test2'] == 3.1


def test_receive_msgpack_with_slot_and_parameters(communicator2) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MCPMessage(
            Reference('kernel[13].out'), Reference('other.in[13]'),
            0.0, 1.0,
            msgpack.packb({'test': 'testing'}), msgpack.packb('test'))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator2._Communicator__get_client = get_client_mock

    msg = communicator2.receive_message('in', 13)

    get_client_mock.assert_called_with(Reference('kernel[13]'))
    client_mock.receive.assert_called_with(Reference('other.in[13]'))
    assert msg.data == 'test'
    assert msg.configuration['test'] == 'testing'


def test_receive_configuration(communicator) -> None:
    client_mock = MagicMock()
    config_dict = {'test': 13}
    config_data = msgpack.ExtType(1, msgpack.packb(config_dict,
                                                   use_bin_type=True))
    client_mock.receive.return_value = MCPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            0.0, None, msgpack.packb({'test1': 12}),
            msgpack.packb(config_data))
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock

    msg = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert isinstance(msg.data, Configuration)
    assert msg.data['test'] == 13


def test_close_port(communicator) -> None:
    communicator.close_port('out')

    assert 'other.in[13]' in communicator._Communicator__outboxes
    msg = communicator._Communicator__outboxes[
            'other.in[13]']._Outbox__queue[0]
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.timestamp == float('inf')
    assert msg.next_timestamp is None
    assert msg.parameter_overlay == msgpack.packb({}, use_bin_type=True)
    unpacked = msgpack.unpackb(msg.data, raw=False)
    assert isinstance(unpacked, msgpack.ExtType)
    assert unpacked[0] == 0


def test_get_message(communicator, message) -> None:
    communicator.send_message('out', message)
    assert communicator.get_message('other.in[13]').data == msgpack.packb(
            b'test', use_bin_type=True)


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
