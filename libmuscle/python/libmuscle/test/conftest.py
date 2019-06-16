import pytest
from unittest.mock import patch

from ymmsl import Settings

from libmuscle.communicator import Message
from libmuscle.mmp_client import MMPClient


@pytest.fixture
def mock_grpc_channel():
    with patch('libmuscle.mmp_client.grpc.insecure_channel'):
        yield None


@pytest.fixture
def mocked_mmp_client(mock_grpc_channel):
    with patch('libmuscle.mmp_client.grpc.insecure_channel'), \
         patch('libmuscle.mmp_client.grpc.channel_ready_future'), \
         patch('muscle_manager_protocol.' +
               'muscle_manager_protocol_pb2_grpc.MuscleManagerStub'
               ) as mock_stub:

        stub = mock_stub.return_value
        yield MMPClient(''), stub


@pytest.fixture
def message() -> Message:
    return Message(0.0, None, b'test', Settings())


@pytest.fixture
def message2() -> Message:
    return Message(0.0, None, {'test': 17}, Settings())
