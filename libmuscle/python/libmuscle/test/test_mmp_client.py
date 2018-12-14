from unittest.mock import patch

import pytest
from ymmsl import Port, Reference

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
            Operator.NONE,
            Timestamp(1.0),
            LogLevel.WARNING,
            'Testing the MMPClient')

    mocked_mmp_client[0].submit_log_message(message)
    assert mocked_mmp_client[1].SubmitLogMessage.called


def test_register_instance(mocked_mmp_client) -> None:
    mocked_mmp_client[0].register_instance(
            Reference('kernel[13]'),
            ['direct:test', 'tcp:test'],
            [Port('out', Operator.O_I), Port('in', Operator.S)])
    assert mocked_mmp_client[1].RegisterInstance.called
