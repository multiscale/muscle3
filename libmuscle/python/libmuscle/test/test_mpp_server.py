from unittest.mock import MagicMock, patch

import pytest

from libmuscle.mpp_server import MPPServer


@pytest.fixture(autouse=True)
def PostOffice():
    with patch('libmuscle.mpp_server.PostOffice') as PostOffice:
        yield PostOffice


@pytest.fixture
def MockTransportServer():
    MockTransportServer = MagicMock()
    transport_server = MockTransportServer.return_value
    transport_server.get_location.return_value = 'tcp:testing:9001'
    return MockTransportServer


@pytest.fixture(autouse=True)
def transport_server_types(MockTransportServer):
    with patch('libmuscle.mpp_server.transport_server_types', [MockTransportServer]):
        yield None


@pytest.fixture
def transport_server(MockTransportServer):
    return MockTransportServer.return_value


@pytest.fixture
def mpp_server():
    return MPPServer()


def test_get_locations(mpp_server, transport_server):
    assert mpp_server.get_locations() == [transport_server.get_location.return_value]
