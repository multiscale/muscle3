import pytest
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Operator, Port, Timeline
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import TimelineManager

INSTANCE_NAME = "component"


@pytest.fixture
def port_manager() -> PortManager:
    """Port manager with all four operator types across named and unnamed timelines."""
    pm = PortManager([], None)
    peer_info = PeerInfo(
        Ref(INSTANCE_NAME),
        [],
        [],
        {},
        {},
        [
            Port(Id("out_macro"), Operator.O_I, Timeline(":macro")),
            Port(Id("out_no_tl"), Operator.O_I),
            Port(Id("in_micro"), Operator.S, Timeline(":micro")),
            Port(Id("out_f"), Operator.O_F, Timeline(":output_tl")),
            Port(Id("in_f"), Operator.F_INIT),
        ],
    )
    pm.connect_ports(peer_info)
    return pm


def test_init(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    assert tm._iteration is None
    assert set(tm._sub_timelines.keys()) == {
            Timeline(":macro"), Timeline(":micro"), Timeline(":" + INSTANCE_NAME)}


def test_sub_timeline_manager_init(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    assert tm._sub_timelines[Timeline(":" + INSTANCE_NAME)]._iteration is None
    assert tm._sub_timelines[Timeline(":macro")]._iteration is None
    assert tm._sub_timelines[Timeline(":micro")]._iteration is None
