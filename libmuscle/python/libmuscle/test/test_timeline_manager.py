import pytest
from ymmsl.v0_2 import Conduit, Operator, Port, Timeline
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import (
    AlreadyParticipated,
    MessageOutOfSync,
    PortBlocked,
    ReuseLoopIncomplete,
    TimelineManager,
    TimelinePorts,
)


def _build_component_port_manager(
    has_f_init: bool = True, include_settings: bool = True
) -> PortManager:
    conduits = [
        Conduit("component.out_f", "peer_f.in"),
        Conduit("component.out_a1", "peer_a1.in"),
        Conduit("peer_a1.out", "component.in_a1"),
        Conduit("peer_a1_2.out", "component.in_a1_2"),
        Conduit("component.out_a2", "peer_a2.in"),
        Conduit("component.out_a2_2", "peer_a2_2.in"),
        Conduit("peer_a2.out", "component.in_a2"),
    ]
    peer_dims = {
        Ref("peer_f"): [],
        Ref("peer_a1"): [],
        Ref("peer_a1_2"): [],
        Ref("peer_a2"): [],
        Ref("peer_a2_2"): [],
    }
    ymmsl_ports = [
        Port(Id("out_f"), Operator.O_F),
        Port(Id("out_a1"), Operator.O_I, Timeline(":A1")),
        Port(Id("in_a1"), Operator.S, Timeline(":A1")),
        Port(Id("in_a1_2"), Operator.S, Timeline(":A1")),
        Port(Id("out_a2"), Operator.O_I, Timeline(":A2")),
        Port(Id("out_a2_2"), Operator.O_I, Timeline(":A2")),
        Port(Id("in_a2"), Operator.S, Timeline(":A2")),
    ]
    if has_f_init:
        conduits.append(Conduit("peer_init.out", "component.in_f"))
        peer_dims[Ref("peer_init")] = []
        ymmsl_ports.append(Port(Id("in_f"), Operator.F_INIT))
    if include_settings:
        conduits.append(Conduit("peer_settings.out", "component.muscle_settings_in"))
        peer_dims[Ref("peer_settings")] = []

    pm = PortManager([], None)
    peer_info = PeerInfo(Ref("component"), [], conduits, peer_dims, {}, ymmsl_ports)
    pm.connect_ports(peer_info)
    return pm


@pytest.fixture
def port_manager() -> PortManager:
    return _build_component_port_manager()


@pytest.fixture
def timeline_manager(port_manager: PortManager) -> TimelineManager:
    return TimelineManager(port_manager)


def test_init(timeline_manager: TimelineManager) -> None:
    assert timeline_manager._iteration is None
    assert timeline_manager._send is None
    assert timeline_manager._receive is None
    assert timeline_manager._submanagers == {}


@pytest.mark.parametrize("settings_connected", [True, False])
def test_on_ports_connected(settings_connected: bool) -> None:
    pm = _build_component_port_manager(include_settings=settings_connected)
    tm = TimelineManager(pm)
    tm.on_ports_connected()

    assert isinstance(tm._send, TimelinePorts)
    assert isinstance(tm._receive, TimelinePorts)

    expected_receive = {("in_f", Operator.F_INIT)}
    if settings_connected:
        expected_receive.add(("muscle_settings_in", Operator.F_INIT))

    assert {
        (str(port.name), port.operator) for port in tm._receive.ports
    } == expected_receive
    assert {(str(port.name), port.operator) for port in tm._send.ports} == {
        ("out_f", Operator.O_F)
    }


def test_on_ports_connected_timeline_ports(timeline_manager: TimelineManager) -> None:
    timeline_manager.on_ports_connected()
    assert timeline_manager._receive.num_slots == 2
    assert timeline_manager._send.num_slots == 1
    assert timeline_manager._send.participated == set()
    assert timeline_manager._receive.participated == set()

    assert set(timeline_manager._submanagers.keys()) == {
        Timeline(":A1"),
        Timeline(":A2"),
    }


@pytest.mark.parametrize("has_f_init", [True, False])
def test_on_ports_connected_sets_initial_iteration(has_f_init: bool) -> None:
    pm = _build_component_port_manager(has_f_init=has_f_init, include_settings=False)
    tm = TimelineManager(pm)
    tm.on_ports_connected()
    assert tm._iteration == (None if has_f_init else [])


def test_subtimeline_manager_initialization() -> None:
    pm = _build_component_port_manager()
    tm = TimelineManager(pm)
    tm.on_ports_connected()

    stm_a1 = tm._submanagers[Timeline(":A1")]
    assert stm_a1._iteration is None
    assert stm_a1._first_operator is None
    assert {str(port.name) for port in stm_a1._send.ports} == {"out_a1"}
    assert {str(port.name) for port in stm_a1._receive.ports} == {"in_a1", "in_a1_2"}

    stm_a2 = tm._submanagers[Timeline(":A2")]
    assert stm_a2._iteration is None
    assert stm_a2._first_operator is None
    assert {str(port.name) for port in stm_a2._send.ports} == {"out_a2", "out_a2_2"}
    assert {str(port.name) for port in stm_a2._receive.ports} == {"in_a2"}


def test_check_send_message_o_f_blocked_when_subtimeline_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    # receive on the F_INIT ports
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so the :A1 sub-timeline is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_f")

    port_in_a1 = timeline_manager._port_manager.get_port("in_a1")
    port_in_a1_2 = timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.expected == [
        ("receive", port_in_a1, []),
        ("receive", port_in_a1_2, []),
    ]


def test_check_send_message_o_f_raises_already_participated_when_sent_twice(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    # receive on the F_INIT ports
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    # skipping the subtimelines is allowed
    timeline_manager.check_send_message("out_f")

    with pytest.raises(AlreadyParticipated) as exc_info:
        timeline_manager.check_send_message("out_f")

    assert exc_info.value.port == timeline_manager._port_manager.get_port("out_f")
    assert exc_info.value.slot is None
    assert exc_info.value.action == "send"


def test_check_send_message_o_f_marks_participated_and_returns_iteration(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])

    assert not timeline_manager._send.has_participated("out_f", None)
    iteration = timeline_manager.check_send_message("out_f")
    assert iteration == []
    assert iteration == timeline_manager._iteration
    assert timeline_manager._send.has_participated("out_f", None)


def test_check_send_message_o_i_starts_subtimeline_with_o_i_leading(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])

    iteration = timeline_manager.check_send_message("out_a1")

    stm = timeline_manager._submanagers[Timeline(":A1")]
    assert stm._first_operator is Operator.O_I
    assert stm._iteration == [0]
    assert iteration == [0]
    assert stm._send.has_participated("out_a1", None)


def test_check_send_message_o_i_blocked_when_s_leads_and_not_all_s_received(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_receive("in_a1")
    timeline_manager.check_received_message("in_a1", None, [0])
    # "in_a1_2" never received, so S hasn't fully led :A1 yet

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_a1")

    port_in_a1_2 = timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.expected == [("receive", port_in_a1_2, [])]


def test_check_send_message_o_i_allowed_once_all_led_s_ports_received(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_receive("in_a1")
    timeline_manager.check_received_message("in_a1", None, [0])
    timeline_manager.check_receive("in_a1_2")
    timeline_manager.check_received_message("in_a1_2", None, [0])

    iteration = timeline_manager.check_send_message("out_a1")

    stm = timeline_manager._submanagers[Timeline(":A1")]
    assert stm._first_operator is Operator.S
    assert stm._iteration == [0]
    assert iteration == [0]
    assert stm._send.has_participated("out_a1", None)

    # A second send on out_a1 cannot advance the sub-iteration itself: with S
    # leading, only a new S receive is allowed to do that.
    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_a1")

    port_in_a1 = timeline_manager._port_manager.get_port("in_a1")
    port_in_a1_2 = timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.expected == [
        ("receive", port_in_a1, []),
        ("receive", port_in_a1_2, []),
    ]


def test_check_send_message_o_i_when_o_i_leads_and_complete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])

    first_iteration = timeline_manager.check_send_message("out_a1")
    timeline_manager.check_receive("in_a1")
    timeline_manager.check_received_message("in_a1", None, first_iteration)
    timeline_manager.check_receive("in_a1_2")
    timeline_manager.check_received_message("in_a1_2", None, first_iteration)

    second_iteration = timeline_manager.check_send_message("out_a1")

    stm = timeline_manager._submanagers[Timeline(":A1")]
    assert first_iteration == [0]
    assert second_iteration == [1]
    assert stm._iteration == [1]
    assert stm._send.participated == {("out_a1", None)}
    assert stm._receive.participated == set()


def test_check_send_message_o_i_blocked_when_o_i_leads_and_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so the sub-iteration is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_a1")

    port_in_a1 = timeline_manager._port_manager.get_port("in_a1")
    port_in_a1_2 = timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.expected == [
        ("receive", port_in_a1, []),
        ("receive", port_in_a1_2, []),
    ]


def test_check_receive_f_init_allowed_when_not_yet_participated(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    assert not timeline_manager._receive.has_participated("in_f", None)

    timeline_manager.check_received_message("in_f", None, [3])
    assert timeline_manager._iteration == [3]
    assert timeline_manager._receive.has_participated("in_f", None)

    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [3])

    assert timeline_manager._iteration == [3]
    assert timeline_manager._receive.has_participated("muscle_settings_in", None)


def test_check_receive_f_init_raises_already_participated_when_received_twice(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])

    with pytest.raises(AlreadyParticipated) as exc_info:
        timeline_manager.check_receive("in_f")

    assert exc_info.value.port == timeline_manager._port_manager.get_port("in_f")
    assert exc_info.value.slot is None
    assert exc_info.value.action == "receive"


def test_check_received_message_f_init_raises_when_iteration_differs(
    timeline_manager: TimelineManager,
) -> None:
    """Once the main timeline has started, an F_INIT message for a different
    iteration is rejected."""
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [3])
    timeline_manager.check_receive("muscle_settings_in")

    with pytest.raises(MessageOutOfSync) as exc_info:
        timeline_manager.check_received_message("muscle_settings_in", None, [4])

    assert exc_info.value.port == timeline_manager._port_manager.get_port(
        "muscle_settings_in"
    )
    assert exc_info.value.slot is None


def test_check_receive_message_s_starts_subtimeline_with_s_leading(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])

    timeline_manager.check_receive("in_a2")
    timeline_manager.check_received_message("in_a2", None, [0])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    assert stm._first_operator is Operator.S
    assert stm._iteration == [0]
    assert stm._receive.has_participated("in_a2", None)


def test_check_receive_message_s_blocked_when_o_i_leads_and_not_all_o_i_sent(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_send_message("out_a2")
    # "out_a2_2" never sent, so O_I hasn't fully led :A2 yet

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive("in_a2")

    port_out_a2_2 = timeline_manager._port_manager.get_port("out_a2_2")
    assert exc_info.value.expected == [("send", port_out_a2_2, [])]


def test_check_receive_message_s_allowed_once_all_led_o_i_ports_sent(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_send_message("out_a2")
    timeline_manager.check_send_message("out_a2_2")

    timeline_manager.check_receive("in_a2")
    timeline_manager.check_received_message("in_a2", None, [0])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    assert stm._first_operator is Operator.O_I
    assert stm._iteration == [0]
    assert stm._receive.has_participated("in_a2", None)

    # A second receive on in_a2 cannot advance the sub-iteration itself: with O_I
    # leading, only a new O_I send is allowed to do that.
    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive("in_a2")

    port_out_a2 = timeline_manager._port_manager.get_port("out_a2")
    port_out_a2_2 = timeline_manager._port_manager.get_port("out_a2_2")
    assert exc_info.value.expected == [
        ("send", port_out_a2, []),
        ("send", port_out_a2_2, []),
    ]


def test_check_receive_message_s_when_s_leads_and_complete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])

    timeline_manager.check_receive("in_a2")
    timeline_manager.check_received_message("in_a2", None, [1])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    first_iteration = stm._iteration

    timeline_manager.check_send_message("out_a2")
    timeline_manager.check_send_message("out_a2_2")
    timeline_manager.check_receive("in_a2")
    timeline_manager.check_received_message("in_a2", None, [3])

    second_iteration = stm._iteration

    assert first_iteration == [1]
    assert second_iteration == [3]
    assert stm._send.participated == set()
    assert stm._receive.participated == {("in_a2", None)}


def test_check_receive_message_s_blocked_when_s_leads_and_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [])
    timeline_manager.check_receive("in_a2")
    timeline_manager.check_received_message("in_a2", None, [1])
    # neither "out_a2" nor "out_a2_2" received, so the sub-iteration is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive("in_a2")

    port_out_a2 = timeline_manager._port_manager.get_port("out_a2")
    port_out_a2_2 = timeline_manager._port_manager.get_port("out_a2_2")
    assert exc_info.value.expected == [
        ("send", port_out_a2, []),
        ("send", port_out_a2_2, []),
    ]


def test_finish_reuse_iteration_resets_when_complete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()

    # Drive one full reuse loop iteration, using :A1's sub-timeline, to
    # completion.
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [3])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [3])
    timeline_manager.check_send_message("out_a1")
    timeline_manager.check_receive("in_a1")
    timeline_manager.check_received_message("in_a1", None, [3, 0])
    timeline_manager.check_receive("in_a1_2")
    timeline_manager.check_received_message("in_a1_2", None, [3, 0])
    # :A2 is never touched this iteration, which is fine: an untouched
    # sub-timeline is considered complete.
    timeline_manager.check_send_message("out_f")

    timeline_manager.finish_reuse_iteration()

    assert timeline_manager._iteration is None
    assert timeline_manager._send.participated == set()
    assert timeline_manager._receive.participated == set()
    for stm in timeline_manager._submanagers.values():
        assert stm._iteration is None
        assert stm._first_operator is None
        assert stm._send.participated == set()
        assert stm._receive.participated == set()


def test_finish_reuse_iteration_raises_when_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()

    # Start a reuse loop iteration but leave it incomplete: :A1's
    # sub-timeline is started but never finishes, and O_F never sends.
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [4])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [4])
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so :A1 is incomplete, and
    # "out_f" is never sent either

    with pytest.raises(ReuseLoopIncomplete) as exc_info:
        timeline_manager.finish_reuse_iteration()

    port_out_f = timeline_manager._port_manager.get_port("out_f")
    port_in_a1 = timeline_manager._port_manager.get_port("in_a1")
    port_in_a1_2 = timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.expected == [
        ("send", port_out_f, []),
        ("receive", port_in_a1, []),
        ("receive", port_in_a1_2, []),
    ]


def test_get_state_and_restore_state_round_trip(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.on_ports_connected()
    timeline_manager.check_receive("in_f")
    timeline_manager.check_received_message("in_f", None, [3])
    timeline_manager.check_receive("muscle_settings_in")
    timeline_manager.check_received_message("muscle_settings_in", None, [3])
    timeline_manager.check_send_message("out_a1")
    timeline_manager.check_receive("in_a1")
    timeline_manager.check_received_message("in_a1", None, [3, 0])
    # "in_a1_2" not yet received, so :A1 is incomplete, and "out_f" not yet sent

    timeline_state = timeline_manager.get_state()

    # Restore into a fresh TimelineManager, as would happen after loading a
    # snapshot in a new process, from an independent but identically
    # configured PortManager.
    restored = TimelineManager(_build_component_port_manager())
    restored.on_ports_connected()
    restored.restore_state(timeline_state)

    assert restored._iteration == timeline_manager._iteration
    assert restored._send.participated == timeline_manager._send.participated
    assert restored._receive.participated == timeline_manager._receive.participated
    for tl, stm in timeline_manager._submanagers.items():
        restored_stm = restored._submanagers[tl]
        assert restored_stm._iteration == stm._iteration
        assert restored_stm._first_operator == stm._first_operator
        assert restored_stm._send.participated == stm._send.participated
        assert restored_stm._receive.participated == stm._receive.participated
