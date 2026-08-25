from typing import Optional

import pytest
from ymmsl.v0_2 import Conduit, Operator, Port, Timeline
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import (
    AlreadyParticipated,
    ExpectedActions,
    IterationCount,
    MessageOutOfSync,
    PortBlocked,
    ReuseLoopIncomplete,
    TimelineManager,
    is_subiteration,
)


@pytest.fixture
def has_f_init(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param", True)


@pytest.fixture
def include_settings(request: pytest.FixtureRequest) -> bool:
    return getattr(request, "param", True)


@pytest.fixture
def timeline_manager(has_f_init: bool, include_settings: bool) -> TimelineManager:
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

    return TimelineManager(pm)


@pytest.fixture
def vector_timeline_manager() -> TimelineManager:
    declared_ports = {Operator.O_F: ["out_v[]"]}
    pm = PortManager([], declared_ports)
    conduits = [Conduit("component.out_v", "peer.in")]
    peer_info = PeerInfo(Ref("component"), [], conduits, {Ref("peer"): [3]}, {}, [])
    pm.connect_ports(peer_info)

    tm = TimelineManager(pm)
    return tm


def expected(
    timeline_manager: TimelineManager, *actions: tuple[str, str, list[int]]
) -> ExpectedActions:
    return [
        (action, timeline_manager._port_manager.get_port(port_name), slots)
        for action, port_name, slots in actions
    ]


def check_received(
    timeline_manager: TimelineManager,
    port: str,
    slot: Optional[int],
    iteration: IterationCount,
) -> None:
    timeline_manager.check_receive_s(port, slot)
    timeline_manager.record_received_s_message(port, slot, iteration)


def test_is_subiteration():
    assert is_subiteration([], [])
    assert is_subiteration([1, 2], [1, 2])
    assert is_subiteration([1, 2], [1])
    assert is_subiteration([1, 2], [])
    assert not is_subiteration([1, 2], [1, 2, 3])
    assert not is_subiteration([1, 2], [1, 1])


@pytest.mark.parametrize("include_settings", [False], indirect=True)
def test_finish_reuse_iteration_ignores_muscle_settings_in_when_disconnected(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations({("in_f", None): []})
    timeline_manager.check_send_message("out_f")

    timeline_manager.finish_reuse_iteration()


@pytest.mark.parametrize("has_f_init", [False], indirect=True)
@pytest.mark.parametrize("include_settings", [False], indirect=True)
def test_o_f_can_send_immediately_when_no_f_init_connections(
    timeline_manager: TimelineManager,
) -> None:
    assert timeline_manager.check_send_message("out_f") == []


def test_check_send_message_o_f_blocked_when_subtimeline_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    # receive on the F_INIT ports
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so the :A1 sub-timeline is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_f")

    assert exc_info.value.expected == expected(
        timeline_manager, ("receive", "in_a1", []), ("receive", "in_a1_2", [])
    )


def test_check_send_message_o_f_raises_already_participated_when_sent_twice(
    timeline_manager: TimelineManager,
) -> None:
    # receive on the F_INIT ports
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
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
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )

    assert not timeline_manager._send.has_participated("out_f", None)
    iteration = timeline_manager.check_send_message("out_f")
    assert iteration == []
    assert iteration == timeline_manager._iteration
    assert timeline_manager._send.has_participated("out_f", None)


def test_check_send_message_o_i_starts_subtimeline_with_o_i_leading(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )

    iteration = timeline_manager.check_send_message("out_a1")

    stm = timeline_manager._submanagers[Timeline(":A1")]
    assert stm._first_operator is Operator.O_I
    assert stm._iteration == [0]
    assert iteration == [0]
    assert stm._send.has_participated("out_a1", None)


def test_check_send_message_o_i_blocked_when_s_leads_and_not_all_s_received(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    check_received(timeline_manager, "in_a1", None, [0])
    # "in_a1_2" never received, so S hasn't fully led :A1 yet

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_a1")

    assert exc_info.value.expected == expected(
        timeline_manager, ("receive", "in_a1_2", [])
    )


def test_check_send_message_o_i_allowed_once_all_led_s_ports_received(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    check_received(timeline_manager, "in_a1", None, [0])

    timeline_manager.check_receive_s("in_a1_2")
    with pytest.raises(MessageOutOfSync) as exc_info:
        timeline_manager.record_received_s_message("in_a1_2", None, [7])
    assert exc_info.value.port == timeline_manager._port_manager.get_port("in_a1_2")
    assert exc_info.value.slot is None

    check_received(timeline_manager, "in_a1_2", None, [0])

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

    assert exc_info.value.expected == expected(
        timeline_manager, ("receive", "in_a1", []), ("receive", "in_a1_2", [])
    )


def test_check_send_message_o_i_when_o_i_leads_and_complete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )

    first_iteration = timeline_manager.check_send_message("out_a1")
    timeline_manager.check_receive_s("in_a1")
    timeline_manager.record_received_s_message("in_a1", None, first_iteration)
    timeline_manager.check_receive_s("in_a1_2")
    timeline_manager.record_received_s_message("in_a1_2", None, first_iteration)

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
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so the sub-iteration is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_send_message("out_a1")

    assert exc_info.value.expected == expected(
        timeline_manager, ("receive", "in_a1", []), ("receive", "in_a1_2", [])
    )


@pytest.mark.parametrize("iterationcount", ([], [1], [4], [1, 2, 3, 4]))
def test_check_finit_iterations(
    timeline_manager: TimelineManager, iterationcount: IterationCount
) -> None:
    result = timeline_manager.check_f_init_iterations(
        {
            ("in_f", None): iterationcount.copy(),
            ("muscle_settings_in", None): iterationcount.copy(),
        }
    )
    assert result == iterationcount


def test_check_finit_iterations_when_iteration_differs(
    timeline_manager: TimelineManager,
) -> None:
    """All F_INIT messages should have the same iteration count."""
    with pytest.raises(RuntimeError, match="parallel timelines"):
        timeline_manager.check_f_init_iterations(
            {("in_f", None): [3], ("muscle_settings_in", None): [4]}
        )


def test_check_receive_message_s_starts_subtimeline_with_s_leading(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )

    check_received(timeline_manager, "in_a2", None, [0])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    assert stm._first_operator is Operator.S
    assert stm._iteration == [0]
    assert stm._receive.has_participated("in_a2", None)


def test_check_receive_message_s_blocked_when_o_i_leads_and_not_all_o_i_sent(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    timeline_manager.check_send_message("out_a2")
    # "out_a2_2" never sent, so O_I hasn't fully led :A2 yet

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive_s("in_a2")

    assert exc_info.value.expected == expected(
        timeline_manager, ("send", "out_a2_2", [])
    )


def test_check_receive_message_s_allowed_once_all_led_o_i_ports_sent(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    timeline_manager.check_send_message("out_a2")
    timeline_manager.check_send_message("out_a2_2")

    check_received(timeline_manager, "in_a2", None, [0])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    assert stm._first_operator is Operator.O_I
    assert stm._iteration == [0]
    assert stm._receive.has_participated("in_a2", None)

    # A second receive on in_a2 cannot advance the sub-iteration itself: with O_I
    # leading, only a new O_I send is allowed to do that.
    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive_s("in_a2")

    assert exc_info.value.expected == expected(
        timeline_manager, ("send", "out_a2", []), ("send", "out_a2_2", [])
    )


def test_check_receive_message_s_when_s_leads_and_complete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )

    check_received(timeline_manager, "in_a2", None, [1])

    stm = timeline_manager._submanagers[Timeline(":A2")]
    first_iteration = stm._iteration

    timeline_manager.check_send_message("out_a2")
    timeline_manager.check_send_message("out_a2_2")

    timeline_manager.check_receive_s("in_a2")
    with pytest.raises(MessageOutOfSync) as exc_info:
        timeline_manager.record_received_s_message("in_a2", None, first_iteration)
    assert exc_info.value.port == timeline_manager._port_manager.get_port("in_a2")
    assert exc_info.value.slot is None

    check_received(timeline_manager, "in_a2", None, [3])

    second_iteration = stm._iteration

    assert first_iteration == [1]
    assert second_iteration == [3]
    assert stm._send.participated == set()
    assert stm._receive.participated == {("in_a2", None)}


def test_check_receive_message_s_blocked_when_s_leads_and_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    timeline_manager.check_f_init_iterations(
        {("in_f", None): [], ("muscle_settings_in", None): []}
    )
    check_received(timeline_manager, "in_a2", None, [1])
    # neither "out_a2" nor "out_a2_2" received, so the sub-iteration is incomplete

    with pytest.raises(PortBlocked) as exc_info:
        timeline_manager.check_receive_s("in_a2")

    assert exc_info.value.expected == expected(
        timeline_manager, ("send", "out_a2", []), ("send", "out_a2_2", [])
    )


def test_finish_reuse_iteration_resets_when_complete(
    timeline_manager: TimelineManager,
) -> None:
    # Drive one full reuse loop iteration, using :A1's sub-timeline, to
    # completion.
    assert timeline_manager.check_f_init_iterations(
        {("in_f", None): [3], ("muscle_settings_in", None): [3]}
    ) == [3]
    timeline_manager.check_send_message("out_a1")
    check_received(timeline_manager, "in_a1", None, [3, 0])
    check_received(timeline_manager, "in_a1_2", None, [3, 0])
    # :A2 is never touched this iteration, which is fine: an untouched
    # sub-timeline is considered complete.
    timeline_manager.check_send_message("out_f")

    timeline_manager.finish_reuse_iteration()

    # A fresh, just-connected TimelineManager has never participated in
    # anything, so comparing against its state confirms everything was reset.
    fresh = TimelineManager(timeline_manager._port_manager)
    assert timeline_manager.get_state() == fresh.get_state()


def test_finish_reuse_iteration_raises_when_incomplete(
    timeline_manager: TimelineManager,
) -> None:
    # Start a reuse loop iteration but leave it incomplete: :A1's
    # sub-timeline is started but never finishes, and O_F never sends.
    assert timeline_manager.check_f_init_iterations(
        {("in_f", None): [4], ("muscle_settings_in", None): [4]}
    ) == [4]
    timeline_manager.check_send_message("out_a1")
    # neither "in_a1" nor "in_a1_2" received, so :A1 is incomplete, and
    # "out_f" is never sent either

    with pytest.raises(ReuseLoopIncomplete) as exc_info:
        timeline_manager.finish_reuse_iteration()

    assert exc_info.value.expected == expected(
        timeline_manager,
        ("send", "out_f", []),
        ("receive", "in_a1", []),
        ("receive", "in_a1_2", []),
    )


def test_get_state_and_restore_state_round_trip(
    timeline_manager: TimelineManager,
) -> None:
    assert timeline_manager.check_f_init_iterations(
        {("in_f", None): [3], ("muscle_settings_in", None): [3]}
    ) == [3]
    timeline_manager.check_send_message("out_a1")
    check_received(timeline_manager, "in_a1", None, [3, 0])
    # "in_a1_2" not yet received, so :A1 is incomplete, and "out_f" not yet sent

    timeline_state = timeline_manager.get_state()

    # Restore into a fresh TimelineManager, as would happen after loading a
    # snapshot in a new process, from an independent but identically
    # configured PortManager.
    restored = TimelineManager(timeline_manager._port_manager)
    restored.restore_state(timeline_state)

    assert restored.get_state() == timeline_state


def test_vector_port_slots_participate_independently(
    vector_timeline_manager: TimelineManager,
) -> None:
    tm = vector_timeline_manager
    assert tm.check_send_message("out_v", 0) == []
    assert tm.check_send_message("out_v", 1) == []

    with pytest.raises(AlreadyParticipated) as exc_info:
        tm.check_send_message("out_v", 0)

    assert exc_info.value.port == tm._port_manager.get_port("out_v")
    assert exc_info.value.slot == 0


def test_vector_port_reuse_iteration_incomplete_lists_missing_slots(
    vector_timeline_manager: TimelineManager,
) -> None:
    tm = vector_timeline_manager
    tm.check_send_message("out_v", 0)

    with pytest.raises(ReuseLoopIncomplete) as exc_info:
        tm.finish_reuse_iteration()

    port_out_v = tm._port_manager.get_port("out_v")
    assert exc_info.value.expected == [("send", port_out_v, [1, 2])]
    assert "out_v" in str(exc_info.value)
