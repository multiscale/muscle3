import pytest
from unittest.mock import patch

from ymmsl import Settings

from libmuscle.communicator import Message
from libmuscle.mmp_client import MMPClient


@pytest.fixture
def mocked_mmp_client():
    with patch('libmuscle.mmp_client.TcpTransportClient') as mock_ttc:
        yield MMPClient(''), mock_ttc.return_value


@pytest.fixture
def message() -> Message:
    return Message(0.0, None, b'test', Settings())


@pytest.fixture
def message2() -> Message:
    return Message(0.0, None, {'test': 17}, Settings())
