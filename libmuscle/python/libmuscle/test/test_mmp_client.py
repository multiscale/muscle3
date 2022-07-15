from unittest.mock import patch

import msgpack
import pytest
from ymmsl import Conduit, Operator, Port, Reference

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mcp.protocol import RequestType, ResponseType
from libmuscle.mmp_client import MMPClient


def test_init() -> None:
    with patch('libmuscle.mmp_client.TcpTransportClient') as mock_ttc:
        stub = mock_ttc.return_value
        client = MMPClient('')
        assert client._transport_client == stub     # type: ignore


def test_connection_fail() -> None:
    with patch('libmuscle.mmp_client.CONNECTION_TIMEOUT', 1):
        with pytest.raises(RuntimeError):
            # Port 255 is reserved and privileged, so there's probably
            # nothing there.
            MMPClient('tcp:localhost:255')


def test_submit_log_message(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client
    result = [ResponseType.SUCCESS.value]
    stub.call.return_value = msgpack.packb(result, use_bin_type=True)

    message = LogMessage(
            'test_mmp_client',
            Timestamp(1.0),
            LogLevel.WARNING,
            'Testing the MMPClient')

    client.submit_log_message(message)
    assert stub.call.called

    sent_request = stub.call.call_args[0][0]
    decoded_request = msgpack.unpackb(sent_request, raw=False)

    assert decoded_request == [
            RequestType.SUBMIT_LOG_MESSAGE.value,
            'test_mmp_client', 1.0, LogLevel.WARNING.value,
            'Testing the MMPClient']


def test_get_settings(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    settings_msg = {
            'test1': 'test',
            'test2': 12,
            'test3': 3.14,
            'test4': True,
            'test5': [1.2, 3.4],
            'test6': [[1.2, 3.4], [5.6, 7.8]]}
    transport_result = [ResponseType.SUCCESS.value, settings_msg]
    stub.call.return_value = msgpack.packb(transport_result, use_bin_type=True)

    settings = client.get_settings()
    assert len(settings) == 6
    assert settings['test1'] == 'test'
    assert settings['test2'] == 12
    assert settings['test3'] == 3.14
    assert settings['test4'] is True
    assert settings['test5'] == [1.2, 3.4]
    assert settings['test6'] == [[1.2, 3.4], [5.6, 7.8]]


def test_register_instance(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result = [ResponseType.SUCCESS.value]
    stub.call.return_value = msgpack.packb(result, use_bin_type=True)

    client.register_instance(
            Reference('kernel[13]'),
            ['direct:test', 'tcp:test'],
            [Port('out', Operator.O_I), Port('in', Operator.S)])

    assert stub.call.called
    sent_msg = msgpack.unpackb(stub.call.call_args[0][0], raw=False)
    assert sent_msg == [
            RequestType.REGISTER_INSTANCE.value, 'kernel[13]',
            ['direct:test', 'tcp:test'], [['out', 'O_I'], ['in', 'S']]]


def test_request_peers(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result_msg = [
            ResponseType.SUCCESS.value,
            [['kernel.out', 'other.in']],
            {'other': [20]},
            {'other': ['direct:test', 'tcp:test']}]
    stub.call.return_value = msgpack.packb(result_msg, use_bin_type=True)

    result = client.request_peers(Reference('kernel[13]'))

    assert stub.call.called
    sent_msg = msgpack.unpackb(stub.call.call_args[0][0], raw=False)
    assert sent_msg[0] == RequestType.GET_PEERS.value
    assert sent_msg[1] == 'kernel[13]'

    assert len(result[0]) == 1
    assert isinstance(result[0][0], Conduit)
    assert result[0][0].sender == 'kernel.out'
    assert result[0][0].receiver == 'other.in'

    assert isinstance(result[1], dict)
    assert result[1]['other'] == [20]

    assert isinstance(result[2], dict)
    assert result[2]['other'] == ['direct:test', 'tcp:test']


def test_request_peers_error(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result_msg = [ResponseType.ERROR.value, 'test_error_message']
    stub.call.return_value = msgpack.packb(result_msg, use_bin_type=True)

    with pytest.raises(RuntimeError):
        client.request_peers(Reference('kernel[13]'))


def test_request_peers_timeout(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result_msg = [ResponseType.PENDING.value, 'test_status_message']
    stub.call.return_value = msgpack.packb(result_msg, use_bin_type=True)

    with patch('libmuscle.mmp_client.PEER_TIMEOUT', 1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MIN', 0.1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MAX', 1.0):
        with pytest.raises(RuntimeError):
            client.request_peers(Reference('kernel[13]'))


def test_deregister_instance(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result = [ResponseType.SUCCESS.value]
    stub.call.return_value = msgpack.packb(result, use_bin_type=True)

    client.deregister_instance(Reference('kernel[13]'))

    assert stub.call.called
    sent_msg = msgpack.unpackb(stub.call.call_args[0][0], raw=False)
    assert sent_msg == [RequestType.DEREGISTER_INSTANCE.value, 'kernel[13]']


def test_deregister_instance_error(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    result = [ResponseType.ERROR.value, 'Instance kernel[13] unknown']
    stub.call.return_value = msgpack.packb(result, use_bin_type=True)

    with pytest.raises(RuntimeError):
        client.deregister_instance(Reference('kernel[13]'))

    assert stub.call.called
    sent_msg = msgpack.unpackb(stub.call.call_args[0][0], raw=False)
    assert sent_msg == [RequestType.DEREGISTER_INSTANCE.value, 'kernel[13]']
