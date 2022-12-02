from copy import copy
import pytest
from unittest.mock import patch

from ymmsl import Reference, Settings

from libmuscle.communicator import Message
from libmuscle.mcp.transport_client import ProfileData
from libmuscle.mmp_client import MMPClient
from libmuscle.profiler import Profiler
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


@pytest.fixture
def mocked_profiler():
    class MockMMPClient:
        def __init__(self):
            self.sent_events = None

        def submit_profile_events(self, events):
            self.sent_events = copy(events)

    mock_mmp_client = MockMMPClient()
    yield Profiler(mock_mmp_client), mock_mmp_client
