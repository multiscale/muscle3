from unittest.mock import patch

from libmuscle.logging import LogLevel, LogMessage, Timestamp
from libmuscle.mmp_client import MMPClient
from libmuscle.operator import Operator


def test_init() -> None:
    with patch('grpc.insecure_channel'):
        with patch(
                'libmuscle.manager_protocol.' +
                'muscle_manager_protocol_pb2_grpc.MuscleManagerStub'
                ) as mock_stub:

            stub = mock_stub.return_value
            client = MMPClient()
            assert client._MMPClient__client == stub    # type: ignore


def test_submit_log_message(mocked_mmp_client) -> None:
    message = LogMessage(
            'test_mmp_client',
            Operator.NONE,
            Timestamp(1.0),
            LogLevel.WARNING,
            'Testing the MMPClient')

    mocked_mmp_client[0].submit_log_message(message)
    assert mocked_mmp_client[1].SubmitLogMessage.called
