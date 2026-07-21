from logging import WARNING
from typing import Optional

import pytest
from ymmsl.v0_2 import Conduit, Operator, Port, Timeline
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import (
    TimelineManager,
    _all_ports_participated,
    _reset_participation,
)

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
    tm.connect_subtimelines()
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
    assert tm._ports == []
    assert tm._participated == {}
    assert tm._subtimelines == {}


def test_connect_subtimelines(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.connect_subtimelines()
    assert set(tm._subtimelines.keys()) == {Timeline(":macro"), Timeline(":micro")}


def test_connect_subtimelines_main_ports(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.connect_subtimelines()
    assert {str(port.name) for port in tm._ports} == {"in_f", "out_f"}
    assert tm._participated == {("in_f", None): False, ("out_f", None): False}


def test_subtimeline_manager_init(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.connect_subtimelines()
    assert tm._subtimelines[Timeline(":macro")]._iteration is None
    assert tm._subtimelines[Timeline(":micro")]._iteration is None


def test_subtimeline_manager_participation(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.connect_subtimelines()
    for stm in tm._subtimelines.values():
        assert stm._participated == {
            (str(port.name), None): False for port in stm._ports
        }


def test_participation_helpers(port_manager: PortManager) -> None:
    tm = TimelineManager(port_manager)
    tm.connect_subtimelines()
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
        tm.check_received_message("f_i", [i])
        for _ in range(num_iterations):
            iteration = tm.check_send_message("o_i")
            tm.check_receive("s")
            tm.check_received_message("s", iteration)
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
    tm.check_received_message("f_i", [0])
    iteration = tm.check_send_message("o_i")
    tm.check_receive("s")
    tm.check_received_message("s", iteration)
    tm.check_send_message("o_f")
    assert tm.cycle_complete()
    tm.reset()

    # Second cycle: a cache-like component may skip the sub-timeline
    # entirely, having already used it before.
    tm.check_receive("f_i")
    tm.check_received_message("f_i", [1])
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
    tm.check_received_message("f_i", [0])

    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
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
    tm.check_received_message("f_i", [0])
    tm.check_send_message("o_i")

    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
        tm.check_send_message("o_f")


def test_send_o_i_before_f_init_received_raises() -> None:
    tm = _make_timeline_manager(
        {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"],
        }
    )
    with pytest.raises(RuntimeError, match="must receive on all"):
        tm.check_send_message("o_i")


def test_receive_f_init_twice_in_same_iteration_raises() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    tm.check_receive("f_i")
    tm.check_received_message("f_i", [])

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
    tm.check_received_message("f_i", [])
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
    tm.check_received_message("f_i", [])
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
    tm.check_received_message("f_i", [])

    for i in range(num_iterations):
        tm.check_receive("s")
        tm.check_received_message("s", [i])
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
    tm.check_received_message("f_i", [])
    tm.check_receive("s1")
    tm.check_received_message("s1", [0])

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
    tm.check_received_message("f_i", [])
    tm.check_receive("s")
    tm.check_received_message("s", [0])

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
    tm.check_received_message("f_i", [])
    tm.check_send_message("o_i")

    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
        tm.check_send_message("o_f")


def test_send_o_f_with_unreceived_f_init_port_raises() -> None:
    tm = _make_timeline_manager(
        {Operator.F_INIT: ["f_i1", "f_i2"], Operator.O_F: ["o_f"]}
    )
    tm.check_receive("f_i1")
    tm.check_received_message("f_i1", [])

    with pytest.raises(RuntimeError, match="not all"):
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
        tm.check_received_message("s", iteration)
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()


def test_root_component_with_subtimeline_o_f_first_raises() -> None:
    tm = _make_timeline_manager(
        {Operator.O_I: ["o_i"], Operator.S: ["s"], Operator.O_F: ["o_f"]}
    )
    with pytest.raises(RuntimeError, match="not completed a sub-iteration"):
        tm.check_send_message("o_f")


def test_f_init_and_o_f_only_repeats_then_raises_on_double_receive() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    for i in range(5):
        tm.check_receive("f_i")
        tm.check_received_message("f_i", [i])
        tm.check_send_message("o_f")
        assert tm.cycle_complete()
        tm.reset()

    tm.check_receive("f_i")
    tm.check_received_message("f_i", [5])
    with pytest.raises(RuntimeError, match="already received"):
        tm.check_receive("f_i")


def test_get_state_raises_before_f_init_received() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    with pytest.raises(RuntimeError, match="hasn.t received a message"):
        tm.get_state()


def test_cycle_complete_false_until_every_main_port_participated() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    assert not tm.cycle_complete()

    tm.check_receive("f_i")
    tm.check_received_message("f_i", [0])
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
    tm.check_received_message("f_i", [0])
    iteration = tm.check_send_message("o_i")
    tm.check_receive("s")
    tm.check_received_message("s", iteration)
    tm.check_send_message("o_f")
    assert tm.cycle_complete()

    tm.check_send_message("o_i")
    assert not tm.cycle_complete()


def test_get_state_after_o_f_sent_reflects_completed_cycle_before_reset() -> None:
    tm = _make_timeline_manager({Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    tm.check_receive("f_i")
    tm.check_received_message("f_i", [3])
    tm.check_send_message("o_f")

    assert tm.cycle_complete()
    state = tm.get_state()
    assert state.iteration == [3]

    tm.reset()
    with pytest.raises(RuntimeError, match="hasn.t received a message"):
        tm.get_state()


def test_operator_none_ports_logs_warning(caplog: pytest.LogCaptureFixture) -> None:
    pm = _build_port_manager({Operator.NONE: ["n"]})
    tm = TimelineManager(pm)

    with caplog.at_level(WARNING, logger="libmuscle.timeline_manager"):
        tm.connect_subtimelines()

    assert any(
        "Operator.NONE" in message
        for logger_name, level, message in caplog.record_tuples
        if logger_name == "libmuscle.timeline_manager" and level == WARNING
    )
