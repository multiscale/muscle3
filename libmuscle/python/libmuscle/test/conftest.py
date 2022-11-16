import pytest
from unittest.mock import patch

from ymmsl import Reference, Settings

from libmuscle.communicator import Message
from libmuscle.mcp.transport_client import ProfileData
from libmuscle.mmp_client import MMPClient
from libmuscle.timestamp import Timestamp


@pytest.fixture
def mocked_mmp_client():
    with patch('libmuscle.mmp_client.TcpTransportClient') as mock_ttc:
        yield MMPClient(Reference('component[13]'), ''), mock_ttc.return_value


@pytest.fixture
def message() -> Message:
    return Message(0.0, None, b'test', Settings())


@pytest.fixture
def message2() -> Message:
    return Message(0.0, None, {'test': 17}, Settings())


@pytest.fixture
def profile_data() -> ProfileData:
    return Timestamp(0.0), Timestamp(0.0), Timestamp(0.0)
