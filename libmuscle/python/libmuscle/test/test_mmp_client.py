from unittest.mock import patch

import pytest
from ymmsl import Conduit, Port, Reference

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import MMPClient
from libmuscle.operator import Operator


def test_init() -> None:
    with patch('libmuscle.mmp_client.grpc.insecure_channel'), \
         patch('libmuscle.mmp_client.grpc.channel_ready_future'), \
         patch('muscle_manager_protocol.' +
               'muscle_manager_protocol_pb2_grpc.MuscleManagerStub'
               ) as mock_stub:

        stub = mock_stub.return_value
        client = MMPClient('')
        assert client._MMPClient__client == stub    # type: ignore


def test_connection_fail() -> None:
    with patch('libmuscle.mmp_client.CONNECTION_TIMEOUT', 1):
        with pytest.raises(RuntimeError):
            MMPClient('localhost:9000')


def test_submit_log_message(mocked_mmp_client) -> None:
    message = LogMessage(
            'test_mmp_client',
            Timestamp(1.0),
            LogLevel.WARNING,
            'Testing the MMPClient')

    mocked_mmp_client[0].submit_log_message(message)
    assert mocked_mmp_client[1].SubmitLogMessage.called


def test_get_settings(mocked_mmp_client) -> None:
    client, stub = mocked_mmp_client

    row0 = mmp.ListOfDouble(values=[1.2, 3.4])
    row1 = mmp.ListOfDouble(values=[5.6, 7.8])
    array = mmp.ListOfListOfDouble(values=[row0, row1])
    mmp_values = [
            mmp.Setting(
                name='test1',
                value_type=mmp.SETTING_VALUE_TYPE_STRING,
                value_string='test'),
            mmp.Setting(
                name='test2',
                value_type=mmp.SETTING_VALUE_TYPE_INT,
                value_int=12),
            mmp.Setting(
                name='test3',
                value_type=mmp.SETTING_VALUE_TYPE_FLOAT,
                value_float=3.14),
            mmp.Setting(
                name='test4',
                value_type=mmp.SETTING_VALUE_TYPE_BOOL,
                value_bool=True),
            mmp.Setting(
                name='test5',
                value_type=mmp.SETTING_VALUE_TYPE_LIST_FLOAT,
                value_list_float=mmp.ListOfDouble(values=[1.2, 3.4])),
            mmp.Setting(
                name='test6',
                value_type=mmp.SETTING_VALUE_TYPE_LIST_LIST_FLOAT,
                value_list_list_float=array)]
    settings_result = mmp.SettingsResult(setting_values=mmp_values)
    stub.RequestSettings.return_value = settings_result
    settings = client.get_settings()

    assert len(settings) == 6


def test_register_instance(mocked_mmp_client) -> None:
    mocked_mmp_client[0].register_instance(
            Reference('kernel[13]'),
            ['direct:test', 'tcp:test'],
            [Port('out', Operator.O_I), Port('in', Operator.S)])
    assert mocked_mmp_client[1].RegisterInstance.called


def test_request_peers(mocked_mmp_client) -> None:
    conduits = [mmp.Conduit(sender='kernel.out', receiver='other.in')]
    peer_dimensions = [mmp.PeerResult.PeerDimensions(
            peer_name='other', dimensions=[20])]
    peer_locations = [mmp.PeerResult.PeerLocations(
            instance_name='other', locations=['direct:test', 'tcp:test'])]

    mocked_mmp_client[1].RequestPeers.return_value = mmp.PeerResult(
            status=mmp.RESULT_STATUS_SUCCESS,
            conduits=conduits,
            peer_dimensions=peer_dimensions,
            peer_locations=peer_locations)
    result = mocked_mmp_client[0].request_peers(Reference('kernel[13]'))
    assert mocked_mmp_client[1].RequestPeers.called

    assert len(result[0]) == 1
    assert isinstance(result[0][0], Conduit)
    assert result[0][0].sender == 'kernel.out'
    assert result[0][0].receiver == 'other.in'

    assert isinstance(result[1], dict)
    assert result[1]['other'] == [20]

    assert isinstance(result[2], dict)
    assert result[2]['other'] == ['direct:test', 'tcp:test']


def test_request_peers_error(mocked_mmp_client) -> None:
    mocked_mmp_client[1].RequestPeers.return_value = mmp.PeerResult(
            status=mmp.RESULT_STATUS_ERROR,
            error_message='test_error_message')
    with pytest.raises(RuntimeError):
        mocked_mmp_client[0].request_peers(Reference('kernel[13]'))


def test_request_peers_timeout(mocked_mmp_client) -> None:
    mocked_mmp_client[1].RequestPeers.return_value = mmp.PeerResult(
            status=mmp.RESULT_STATUS_PENDING)
    with patch('libmuscle.mmp_client.PEER_TIMEOUT', 1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MIN', 0.1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MAX', 1.0):
        with pytest.raises(RuntimeError):
            mocked_mmp_client[0].request_peers(Reference('kernel[13]'))
