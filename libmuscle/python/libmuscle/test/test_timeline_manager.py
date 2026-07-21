from typing import Optional

import pytest
from ymmsl.v0_2 import Conduit, Operator, Port, Timeline
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import TimelineManager, _all_participated

INSTANCE_NAME = "component"


def _build_port_manager(
    ports: dict, subtimeline: Optional[Timeline] = None
) -> PortManager:
    """Build a connected PortManager, each port wired to its own dummy peer.

    F_INIT and O_F ports are on the (unnamed) main timeline; O_I and S ports
    all share ``subtimeline``.
    """
    subtimeline = subtimeline if subtimeline is not None else Timeline(":main")
    conduits = []
    peer_dims = {}
    ymmsl_ports = []
    for operator, names in ports.items():
        port_timeline = subtimeline if operator in (Operator.O_I, Operator.S) else None
        for name in names:
            peer = Ref(f"peer_{name}")
            if operator in (Operator.F_INIT, Operator.S):
                conduits.append(Conduit(f"{peer}.out", f"{INSTANCE_NAME}.{name}"))
            else:
                conduits.append(Conduit(f"{INSTANCE_NAME}.{name}", f"{peer}.in"))
            peer_dims[peer] = []
            ymmsl_ports.append(Port(Id(name), operator, port_timeline))

    pm = PortManager([], None)
    peer_info = PeerInfo(Ref(INSTANCE_NAME), [], conduits, peer_dims, {}, ymmsl_ports)
    pm.connect_ports(peer_info)
    return pm


def _make_timeline_manager(
    ports: dict, subtimeline: Optional[Timeline] = None
) -> TimelineManager:
    """Build a fully connected TimelineManager for the given ports."""
    pm = _build_port_manager(ports, subtimeline)
    tm = TimelineManager(pm)
    tm.on_ports_connected()
    return tm


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
    tm = TimelineManager(port_manager)
    assert tm._iteration is None
    assert tm._send_ports == []
    assert tm._receive_ports == []
    assert tm._send_participated == set()
    assert tm._receive_participated == set()
    assert tm._submanagers == {}


def test_on_ports_connected(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.on_ports_connected()
    assert set(tm._submanagers.keys()) == {Timeline(":macro"), Timeline(":micro")}


def test_on_ports_connected_main_ports(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.on_ports_connected()
    assert {str(port.name) for port in tm._receive_ports} == {"in_f"}
    assert {str(port.name) for port in tm._send_ports} == {"out_f"}
    assert tm._num_receive_slots == 1
    assert tm._num_send_slots == 1
    assert tm._send_participated == set()
    assert tm._receive_participated == set()


def test_on_ports_connected_includes_muscle_settings_in() -> None:
    """muscle_settings_in behaves as an F_INIT port (check_receive and
    check_received_message treat it as such), but PortManager.list_ports()
    doesn't return it since it isn't a declared port. TimelineManager must
    track it separately so the "all F_INIT ports participated" counts stay
    correct."""
    pm = PortManager([], None)
    peer_info = PeerInfo(
        Ref(INSTANCE_NAME),
        [],
        [Conduit("peer_settings.out", f"{INSTANCE_NAME}.muscle_settings_in")],
        {Ref("peer_settings"): []},
        {},
        [],
    )
    pm.connect_ports(peer_info)

    tm = TimelineManager(pm)
    tm.on_ports_connected()

    assert {str(port.name) for port in tm._receive_ports} == {"muscle_settings_in"}
    assert tm._num_receive_slots == 1


def test_subtimeline_manager_init(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.on_ports_connected()
    assert tm._submanagers[Timeline(":macro")]._iteration is None
    assert tm._submanagers[Timeline(":micro")]._iteration is None


def test_subtimeline_manager_participation(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.on_ports_connected()
    for stm in tm._submanagers.values():
        assert stm._send_participated == set()
        assert stm._receive_participated == set()


def test_participation_helpers(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.on_ports_connected()

    assert ("in_f", None) not in tm._receive_participated
    assert not _all_participated(tm._receive_participated, tm._num_receive_slots)
    assert not _all_participated(tm._send_participated, tm._num_send_slots)

    tm._receive_participated.add(("in_f", None))

    assert ("in_f", None) in tm._receive_participated
    assert ("out_f", None) not in tm._send_participated
    assert _all_participated(tm._receive_participated, tm._num_receive_slots)
    assert not _all_participated(tm._send_participated, tm._num_send_slots)

    tm._send_participated.add(("out_f", None))

    assert _all_participated(tm._send_participated, tm._num_send_slots)

    tm._send_participated = set()
    tm._receive_participated = set()

    assert tm._send_participated == set()
    assert tm._receive_participated == set()


@pytest.mark.parametrize("num_iterations", [1, 2])
@pytest.mark.parametrize("num_reuse", [1, 5])
def test_full_cycle_correct(num_iterations: int, num_reuse: int) -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    for i in range(num_reuse):
        tm.check_receive("f_i")
        tm.check_received_message("f_i", None, [i])
        for _ in range(num_iterations):
            iteration = tm.check_send_message("o_i")
            tm.check_receive("s")
            tm.check_received_message("s", None, iteration)
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()


def test_send_o_f_with_previously_used_subtimeline_skipped_ok() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    # First cycle: use the sub-timeline once, establishing it.
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [0])
    iteration = tm.check_send_message("o_i")
    tm.check_receive("s")
    tm.check_received_message("s", None, iteration)
    tm.check_send_message("o_f")
    assert tm.cycle_complete()
    tm.reset()

    # Second cycle: a cache-like component may skip the sub-timeline
    # entirely, having already used it before.
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [1])
    tm.check_send_message("o_f")
    assert tm.cycle_complete()


def test_send_o_f_with_never_used_subtimeline_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [0])

    with pytest.raises(RuntimeError, match="has not been used yet"):
        tm.check_send_message("o_f")


def test_send_o_f_with_incomplete_subtimeline_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [0])
    tm.check_send_message("o_i")

    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
        tm.check_send_message("o_f")


def test_send_o_i_gated_by_muscle_settings_in() -> None:
    """A component with no user-declared F_INIT ports, but with
    muscle_settings_in connected, can send on O_I once muscle_settings_in has
    been received. This is the scenario test_parameter_overlays.py's macro()
    component exercises."""
    conduits = [
        Conduit("peer_settings.out", f"{INSTANCE_NAME}.muscle_settings_in"),
        Conduit(f"{INSTANCE_NAME}.out", "peer_o_i.in"),
        Conduit("peer_s.out", f"{INSTANCE_NAME}.in"),
    ]
    peer_dims = {
        Ref("peer_settings"): [],
        Ref("peer_o_i"): [],
        Ref("peer_s"): [],
    }
    ymmsl_ports = [
        Port(Id("out"), Operator.O_I, Timeline(":sub")),
        Port(Id("in"), Operator.S, Timeline(":sub")),
    ]
    pm = PortManager([], None)
    peer_info = PeerInfo(Ref(INSTANCE_NAME), [], conduits, peer_dims, {}, ymmsl_ports)
    pm.connect_ports(peer_info)

    tm = TimelineManager(pm)
    tm.on_ports_connected()

    tm.check_receive("muscle_settings_in")
    tm.check_received_message("muscle_settings_in", None, [0])

    tm.check_send_message("out")


def test_receive_f_init_twice_in_same_iteration_raises() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])

    with pytest.raises(RuntimeError, match="already received"):
        tm.check_receive("f_i")


def test_receive_s_with_only_some_o_i_sent_raises() -> None:
    # S may receive before any O_I has sent (bridge exception) or once every O_I
    # has sent, but not while only some O_I ports have sent.
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i1", "o_i2"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])
    tm.check_send_message("o_i1")

    with pytest.raises(RuntimeError, match="only some"):
        tm.check_receive("s")


def test_send_o_i_twice_before_s_received_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])
    tm.check_send_message("o_i")

    with pytest.raises(RuntimeError, match="not every port"):
        tm.check_send_message("o_i")


@pytest.mark.parametrize("num_iterations", [1, 2])
def test_full_cycle_s_led_correct(num_iterations: int) -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])

    for i in range(num_iterations):
        tm.check_receive("s")
        tm.check_received_message("s", None, [i])
        tm.check_send_message("o_i")

    tm.check_send_message("o_f")


def test_send_o_i_with_only_some_s_received_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s1", "s2"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])
    tm.check_receive("s1")
    tm.check_received_message("s1", None, [0])

    with pytest.raises(RuntimeError, match="only some"):
        tm.check_send_message("o_i")


def test_receive_s_twice_before_o_i_sent_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])
    tm.check_receive("s")
    tm.check_received_message("s", None, [0])

    with pytest.raises(RuntimeError, match="not every port"):
        tm.check_receive("s")


def test_send_o_f_with_unfinished_subtimeline_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [])
    tm.check_send_message("o_i")

    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
        tm.check_send_message("o_f")


def test_root_o_f_only_repeats_cleanly() -> None:
    tm = _make_timeline_manager({Operator.O_F: ["o_f"]})
    for _ in range(5):
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()


def test_root_component_with_subtimeline_repeats_cleanly() -> None:
    tm = _make_timeline_manager(
        {Operator.O_I: ["o_i"], Operator.S: ["s"], Operator.O_F: ["o_f"]}
    )
    for _ in range(3):
        iteration = tm.check_send_message("o_i")
        tm.check_receive("s")
        tm.check_received_message("s", None, iteration)
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()


def test_root_component_with_subtimeline_o_f_first_raises() -> None:
    tm = _make_timeline_manager(
        {Operator.O_I: ["o_i"], Operator.S: ["s"], Operator.O_F: ["o_f"]}
    )
    with pytest.raises(RuntimeError, match="has not been used yet"):
        tm.check_send_message("o_f")


def test_f_init_and_o_f_only_repeats_then_raises_on_double_receive() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    for i in range(5):
        tm.check_receive("f_i")
        tm.check_received_message("f_i", None, [i])
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()

    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [5])
    with pytest.raises(RuntimeError, match="already received"):
        tm.check_receive("f_i")


def test_cycle_complete_false_until_every_main_port_participated() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    assert not tm.cycle_complete()

    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [0])
    assert not tm.cycle_complete()

    tm.check_send_message("o_f")
    assert tm.cycle_complete()


def test_cycle_complete_false_if_subtimeline_restarts_after_o_f_sent() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [0])
    iteration = tm.check_send_message("o_i")
    tm.check_receive("s")
    tm.check_received_message("s", None, iteration)
    tm.check_send_message("o_f")
    assert tm.cycle_complete()

    tm.check_send_message("o_i")
    assert not tm.cycle_complete()


def test_get_state_after_o_f_sent_reflects_completed_cycle_before_reset() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    tm.check_receive("f_i")
    tm.check_received_message("f_i", None, [3])
    tm.check_send_message("o_f")

    assert tm.cycle_complete()
    state = tm.get_state()
    assert state.iteration == [3]
