import pytest
from ymmsl.v0_2 import Conduit
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Operator, Port, Timeline
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import (
    TimelineManager,
    _all_ports_participated,
    _reset_participation,
)

INSTANCE_NAME = "component"


@pytest.fixture
def port_manager() -> PortManager:
    """Port manager with all four operator types across named timelines.

    Every port has a peer connected via a conduit, since the TimelineManager
    only tracks connected ports (an unconnected port never sends or receives,
    so it can't be required to participate in an iteration).
    """
    pm = PortManager([], None)
    peer_info = PeerInfo(
        Ref(INSTANCE_NAME),
        [],
        [
            Conduit(f"{INSTANCE_NAME}.out_macro", "peer_macro.in"),
            Conduit("peer_micro.out", f"{INSTANCE_NAME}.in_micro"),
            Conduit(f"{INSTANCE_NAME}.out_f", "peer_f.in"),
            Conduit("peer_init.out", f"{INSTANCE_NAME}.in_f"),
        ],
        {
            Ref("peer_macro"): [],
            Ref("peer_micro"): [],
            Ref("peer_f"): [],
            Ref("peer_init"): [],
        },
        {},
        [
            Port(Id("out_macro"), Operator.O_I, Timeline(":macro")),
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
    assert tm._ports == []
    assert tm._participated == {}
    assert tm._sub_timelines == {}


def test_connect_sub_timelines(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    tm.connect_sub_timelines()
    assert set(tm._sub_timelines.keys()) == {Timeline(":macro"), Timeline(":micro")}


def test_connect_sub_timelines_main_ports(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    tm.connect_sub_timelines()
    assert {str(port.name) for port in tm._ports} == {"in_f", "out_f"}
    assert tm._participated == {("in_f", None): False, ("out_f", None): False}


def test_sub_timeline_manager_init(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    tm.connect_sub_timelines()
    assert tm._sub_timelines[Timeline(":macro")]._iteration is None
    assert tm._sub_timelines[Timeline(":micro")]._iteration is None


def test_sub_timeline_manager_participation(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    tm.connect_sub_timelines()
    for stm in tm._sub_timelines.values():
        assert stm._participated == {
            (str(port.name), None): False for port in stm._ports
        }


def test_participation_helpers(port_manager: PortManager) -> None:
    tm = TimelineManager(INSTANCE_NAME, port_manager)
    tm.connect_sub_timelines()
    ports = tm._ports
    participated = tm._participated

    assert not participated[("in_f", None)]
    assert not _all_ports_participated(ports, participated)
    assert _all_ports_participated(ports, participated, Operator.S)

    participated[("in_f", None)] = True

    assert participated[("in_f", None)]
    assert not participated[("out_f", None)]
    assert not _all_ports_participated(ports, participated)
    assert _all_ports_participated(ports, participated, Operator.F_INIT)

    participated[("out_f", None)] = True

    assert _all_ports_participated(ports, participated)

    _reset_participation(participated)

    assert participated == {("in_f", None): False, ("out_f", None): False}
    assert tm._participated == {("in_f", None): False, ("out_f", None): False}
