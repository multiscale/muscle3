from copy import copy
import pytest
from typing import Dict, List, Set, Union
from unittest.mock import patch

from ymmsl import Operator, Reference, Settings

from libmuscle.api_guard import APIGuard
from libmuscle.communicator import Message
from libmuscle.mcp.transport_client import ProfileData
from libmuscle.mmp_client import MMPClient
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources
from libmuscle.port import Port
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
def guard() -> APIGuard:
    return APIGuard(True)


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
    profiler = Profiler(mock_mmp_client)
    yield profiler, mock_mmp_client
    profiler.shutdown()


@pytest.fixture
def profiler_comm_int_10ms():
    with patch('libmuscle.profiler._COMMUNICATION_INTERVAL', 0.01):
        yield None


@pytest.fixture
def declared_ports():
    return {
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.O_I: ['out_v', 'out_r'],
            Operator.S: ['in_v', 'in_r', 'not_connected_v'],
            Operator.O_F: ['out']}


@pytest.fixture
def mock_ports():
    in_port = Port('in', Operator.F_INIT, False, True, 0, [])
    nc_port = Port('not_connected', Operator.F_INIT, False, False, 0, [])
    outv_port = Port('out_v', Operator.O_I, True, True, 0, [13])
    outr_port = Port('out_r', Operator.O_I, True, True, 0, [])
    inv_port = Port('in_v', Operator.S, True, True, 0, [13])
    inr_port = Port('in_r', Operator.S, True, True, 0, [])
    ncv_port = Port('not_connected_v', Operator.S, True, False, 0, [])
    out_port = Port('out', Operator.O_F, False, True, 0, [])

    return {
            'in': in_port, 'not_connected': nc_port, 'out_v': outv_port,
            'out_r': outr_port, 'in_v': inv_port, 'in_r': inr_port,
            'not_connected_v': ncv_port, 'out': out_port}


@pytest.fixture
def connected_port_manager(port_manager, declared_ports, mock_ports):

    def get_port(name):
        return mock_ports[name]

    def port_exists(name):
        return name in mock_ports

    port_manager.get_port = get_port
    port_manager.list_ports.return_value = declared_ports
    port_manager.port_exists = port_exists
    return port_manager


def core(hwthread_id: int) -> Core:
    """Helper that defines a core with the given core and hwthread id."""
    return Core(hwthread_id, {hwthread_id})


def on_node_resources(node_name: str, cores: Union[int, Set[int]]) -> OnNodeResources:
    """Helper that defines resources on a node from the name and a CPU core."""
    if isinstance(cores, int):
        cores = {cores}
    return OnNodeResources(node_name, CoreSet([Core(core, {core}) for core in cores]))


def resources(node_resources: Dict[str, List[Core]]) -> Resources:
    """Helper that defines a Resources from a dict."""
    return Resources([
        OnNodeResources(node_name, CoreSet(cores))
        for node_name, cores in node_resources.items()])
