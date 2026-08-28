from copy import copy
from typing import Union
from unittest.mock import patch

import pytest
from ymmsl.v0_2 import Operator, Reference, Settings

from libmuscle.api_guard import APIGuard
from libmuscle.communicator import Message
from libmuscle.communicator_state import CommunicatorState
from libmuscle.mcp.transport_client import ProfileData
from libmuscle.mmp_client import MMPClient
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources
from libmuscle.port import Port
from libmuscle.port_manager import PortManager
from libmuscle.profiler import Profiler
from libmuscle.timeline_manager import TimelineState
from libmuscle.timestamp import Timestamp


@pytest.fixture
def mocked_mmp_client():
    with patch("libmuscle.mmp_client.TcpTransportClient") as mock_ttc:
        yield MMPClient(Reference("component[13]"), ""), mock_ttc.return_value


@pytest.fixture
def message() -> Message:
    return Message(0.0, None, b"test", Settings())


@pytest.fixture
def message2() -> Message:
    return Message(0.0, None, {"test": 17}, Settings())


@pytest.fixture
def guard() -> APIGuard:
    return APIGuard(True)


@pytest.fixture
def profile_data() -> ProfileData:
    return Timestamp(0.0), Timestamp(0.0), Timestamp(0.0)


@pytest.fixture
def communicator_state() -> CommunicatorState:
    return CommunicatorState(
        port_message_counts={"in": [1], "out": [4], "muscle_settings_in": [0]},
        timeline_state=TimelineState(
            iteration=[1],
            send_participated=[],
            receive_participated=[["in", None]],
            subtimeline_states={},
        ),
    )


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
    with patch("libmuscle.profiler._COMMUNICATION_INTERVAL", 0.01):
        yield None


@pytest.fixture
def declared_ports():
    return {
        Operator.F_INIT: ["in", "not_connected"],
        Operator.O_I: ["out_v", "out_r"],
        Operator.S: ["in_v", "in_r", "not_connected_v"],
        Operator.O_F: ["out"],
    }


@pytest.fixture
def mock_ports():
    in_port = Port("in", Operator.F_INIT, None, False, True, 0, [])
    nc_port = Port("not_connected", Operator.F_INIT, None, False, False, 0, [])
    outv_port = Port("out_v", Operator.O_I, None, True, True, 0, [13])
    outr_port = Port("out_r", Operator.O_I, None, True, True, 0, [])
    inv_port = Port("in_v", Operator.S, None, True, True, 0, [13])
    inr_port = Port("in_r", Operator.S, None, True, True, 0, [])
    ncv_port = Port("not_connected_v", Operator.S, None, True, False, 0, [])
    out_port = Port("out", Operator.O_F, None, False, True, 0, [])

    return {
        "in": in_port,
        "not_connected": nc_port,
        "out_v": outv_port,
        "out_r": outr_port,
        "in_v": inv_port,
        "in_r": inr_port,
        "not_connected_v": ncv_port,
        "out": out_port,
    }


@pytest.fixture
def connected_port_manager(port_manager, declared_ports, mock_ports):

    def get_port(name):
        if name == "muscle_settings_in":
            return port_manager._muscle_settings_in
        return mock_ports[name]

    def port_exists(name):
        return name in mock_ports

    def get_connected_ports(operator, timeline=None):
        # Ensure this returns connected ports based on 'is_connected' of all mock ports
        return PortManager.get_connected_ports(port_manager, operator, timeline)

    port_manager._ports = mock_ports
    port_manager._muscle_settings_in = Port(
        "muscle_settings_in", Operator.F_INIT, None, False, True, 0, []
    )
    port_manager.get_port = get_port
    port_manager.get_connected_ports = get_connected_ports
    port_manager.list_ports.return_value = declared_ports
    port_manager.port_exists = port_exists
    port_manager.has_f_init_connections.return_value = True
    return port_manager


def core(hwthread_id: int) -> Core:
    """Helper that defines a core with the given core and hwthread id."""
    return Core(hwthread_id, {hwthread_id})


def on_node_resources(node_name: str, cores: Union[int, set[int]]) -> OnNodeResources:
    """Helper that defines resources on a node from the name and a CPU core."""
    if isinstance(cores, int):
        cores = {cores}
    return OnNodeResources(node_name, CoreSet([Core(core, {core}) for core in cores]))


def resources(node_resources: dict[str, list[Core]]) -> Resources:
    """Helper that defines a Resources from a dict."""
    return Resources(
        [
            OnNodeResources(node_name, CoreSet(cores))
            for node_name, cores in node_resources.items()
        ]
    )
