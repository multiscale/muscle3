from typing import Union
from unittest.mock import ANY, MagicMock, patch

import pytest
from ymmsl.v0_2 import Conduit, ConduitFilter, Operator, Port, Settings, Timeline
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.communicator import Communicator, Message, PortClosed
from libmuscle.mpp_message import Milestone, MPPMessage
from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import IterationCount


@pytest.fixture
def mpp_client():
    with patch("libmuscle.communicator.MPPClient") as MPPClient:
        yield MPPClient.return_value


@pytest.fixture
def mpp_server():
    with patch("libmuscle.communicator.MPPServer") as MPPServer:
        yield MPPServer.return_value


@pytest.fixture(params=["repeat", "pad"])
def repeat_filter(request):
    return request.param


@pytest.fixture()
def repeater_communicator(repeat_filter, mpp_client):
    port_manager = PortManager([], None)
    mock_manager = MagicMock()
    mock_manager.get_timeline.return_value = Timeline(":parent3:parent2:parent1")
    communicator = Communicator(
        Ref("component"), [], port_manager, MagicMock(), mock_manager
    )
    peer_info = PeerInfo(
        Ref("component"),
        [],
        [
            Conduit("parent1.out", "component.unfiltered"),
            Conduit("parent2.out", "component.repeated", repeat_filter),
            Conduit(
                "parent3.out",
                "component.twicerepeated",
                repeat_filter + " " + repeat_filter,
            ),
            Conduit("parent1.out2", "component.repeated_s", repeat_filter),
        ],
        {Ref("parent1"): [], Ref("parent2"): [], Ref("parent3"): []},
        {Ref("parent1"): [], Ref("parent2"): [], Ref("parent3"): []},
        [
            Port(Id("unfiltered"), Operator.F_INIT),
            Port(Id("repeated"), Operator.F_INIT),
            Port(Id("twicerepeated"), Operator.F_INIT),
            Port(Id("repeated_s"), Operator.S),
        ],
    )
    port_manager.connect_ports(peer_info)
    communicator.set_peer_info(peer_info)
    assert communicator._repeat_filters == {
        "repeated": [ConduitFilter(repeat_filter)],
        "twicerepeated": [ConduitFilter(repeat_filter)] * 2,
        "repeated_s": [ConduitFilter(repeat_filter)],
    }
    yield communicator
    communicator.shutdown()


@pytest.fixture
def reducer_communicator(mpp_client, mpp_server):
    port_manager = PortManager([], None)
    mock_manager = MagicMock()
    mock_manager.get_timeline.return_value = Timeline(":parent")
    communicator = Communicator(
        Ref("component"), [], port_manager, MagicMock(), mock_manager
    )
    peer_info = PeerInfo(
        Ref("component"),
        [],
        [
            Conduit("parent.out", "component.init"),
            Conduit("component.final", "parent.in"),
            Conduit("component.final", "sibling.in2"),
            # Reducer filter on O_I port
            Conduit("component.out", "sibling.in", "last"),
            # Reducer filter on O_F port
            Conduit("component.final", "aunt.init", "last"),
            # Double reducer filter on O_I port
            Conduit("component.out", "uncle.init", "last last"),
        ],
        {Ref("parent"): [], Ref("aunt"): [], Ref("uncle"): [], Ref("sibling"): []},
        {Ref("parent"): [], Ref("aunt"): [], Ref("uncle"): [], Ref("sibling"): []},
        [
            Port(Id("init"), Operator.F_INIT),
            Port(Id("out"), Operator.O_I, Timeline("component")),
            Port(Id("final"), Operator.O_F),
        ],
    )
    port_manager.connect_ports(peer_info)
    communicator.set_peer_info(peer_info)
    assert communicator._reduced_count == {
        "sibling.in": 1,
        "aunt.init": 0,
        "uncle.init": 0,
    }
    yield communicator
    communicator.shutdown()


def mock_receive_messages(
    mpp_client, data: dict[str, list[Union[IterationCount, Milestone]]]
):
    """Helper method to mock MPPClient.receive, so it gives data with correct message
    numbers and iteration counts.

    Args:
        data: A list of IterationCount or Milestone for each port (component.port_name).
            This will end up filling both the MPPMessage.iteration and MPPMessage.data
            fields. MPPMessage.message_number is derived from the number of
            non-Milestone messages sent so far.
    """

    def message_maker(data: list[Union[IterationCount, Milestone]]):
        num = 0
        for item in data:
            iteration = item.iteration if isinstance(item, Milestone) else item
            yield (
                MPPMessage(
                    Ref("snd"),
                    Ref("rcv"),
                    None,
                    0.0,
                    None,
                    Settings(),
                    num,
                    item,
                    iteration,
                ).encoded(),
                MagicMock(),
            )
            if not isinstance(item, Milestone):
                num += 1

    def side_effect(peer, _):
        return next(iterators[peer])

    iterators = {Ref(key): message_maker(value) for key, value in data.items()}
    mpp_client.receive.side_effect = side_effect


def test_repeater_filters(repeater_communicator, mpp_client, repeat_filter):
    twicerepeated_messages = [[0], Milestone([])]
    repeated_messages = [[0, 0], [0, 1], [0, 2], Milestone([0]), Milestone([])]
    unfiltered_messages = [
        [0, 0, 0],
        [0, 0, 1],
        Milestone([0, 0]),
        # parent is allowed to send 0 messages on its O_I port in an iteration
        Milestone([0, 1]),
        [0, 2, 0],
        Milestone([0, 2]),
        Milestone([0]),
        Milestone([]),
    ]
    mock_receive_messages(
        mpp_client,
        {
            "component.twicerepeated": twicerepeated_messages,
            "component.repeated": repeated_messages,
            "component.unfiltered": unfiltered_messages,
            "component.repeated_s": unfiltered_messages,
        },
    )

    is_padded = repeat_filter == "pad"

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [0, 0, 0]
    assert cache[("repeated", None)].data == [0, 0]
    assert cache[("twicerepeated", None)].data == [0]

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [0, 0, 1]
    assert cache[("repeated", None)].data == (None if is_padded else [0, 0])
    assert cache[("twicerepeated", None)].data == (None if is_padded else [0])

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [0, 2, 0]
    assert cache[("repeated", None)].data == [0, 2]
    assert cache[("twicerepeated", None)].data == (None if is_padded else [0])

    with pytest.raises(PortClosed):
        repeater_communicator.pre_receive()


def test_repeater_filters_discard_messages(
    repeater_communicator, mpp_client, repeat_filter
):
    twicerepeated_messages = [[0], [1], [2], Milestone([])]
    repeated_messages = [
        # Grandparent doesn't send on O_I in its first iteration:
        Milestone([0]),
        [1, 0],
        [1, 1],
        [1, 2],
        Milestone([1]),
        [2, 0],
        [2, 1],
        Milestone([2]),
        Milestone([]),
    ]
    unfiltered_messages = [
        Milestone([0]),
        # parent doesn't send messages on O_I in the first couple of iterations
        # component will need to discard the corresponding messages in repeated_messages
        Milestone([1, 0]),
        Milestone([1, 1]),
        Milestone([1, 2]),
        Milestone([1]),
        [2, 0, 0],
        Milestone([2, 0]),
        [2, 1, 0],
        [2, 1, 1],
        Milestone([2, 1]),
        Milestone([2]),
        Milestone([]),
    ]
    mock_receive_messages(
        mpp_client,
        {
            "component.twicerepeated": twicerepeated_messages,
            "component.repeated": repeated_messages,
            "component.unfiltered": unfiltered_messages,
            "component.repeated_s": unfiltered_messages,
        },
    )

    is_padded = repeat_filter == "pad"

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [2, 0, 0]
    assert cache[("repeated", None)].data == [2, 0]
    assert cache[("twicerepeated", None)].data == [2]
    for i in range(3):
        msg = repeater_communicator.receive_s_message("repeated_s")
        assert msg.data == (None if i and is_padded else [2, 0, 0])

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [2, 1, 0]
    assert cache[("repeated", None)].data == [2, 1]
    assert cache[("twicerepeated", None)].data == (None if is_padded else [2])

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [2, 1, 1]
    assert cache[("repeated", None)].data == (None if is_padded else [2, 1])
    assert cache[("twicerepeated", None)].data == (None if is_padded else [2])
    for i in range(3):
        msg = repeater_communicator.receive_s_message("repeated_s")
        assert msg.data == (None if i and is_padded else [2, 1, 1])

    with pytest.raises(PortClosed):
        repeater_communicator.pre_receive()


def test_repeater_filters_no_finit(mpp_client, repeat_filter):
    # Prepare messages before communicator.set_peer_info is called:
    mock_receive_messages(mpp_client, {"component.s_in": [[], Milestone([])]})

    # Prepare a communicator with only a repeated S port and no F_INIT ports:
    port_manager = PortManager([], None)
    communicator = Communicator(
        Ref("component"), [], port_manager, MagicMock(), MagicMock()
    )
    peer_info = PeerInfo(
        Ref("component"),
        [],
        [Conduit("previous.out", "component.s_in", repeat_filter)],
        {Ref("previous"): []},
        {Ref("previous"): []},
        [Port(Id("s_in"), Operator.S)],
    )
    port_manager.connect_ports(peer_info)
    communicator.set_peer_info(peer_info)
    assert communicator._repeat_filters == {
        "s_in": [ConduitFilter(repeat_filter)],
    }

    assert communicator.pre_receive() == {}
    # We can now receive on s_in as often as we'd like
    for i in range(8):
        msg = communicator.receive_s_message("s_in")
        if i == 0 or repeat_filter == "repeat":
            assert msg.data == []
        else:
            assert msg.data is None

    # Cleanup
    communicator.shutdown()


def test_reducer_filters(reducer_communicator, mpp_client, mpp_server):
    mock_receive_messages(mpp_client, {"component.init": [[0], [1], Milestone([])]})

    cache = reducer_communicator.pre_receive()
    assert cache[("init", None)].data == [0]
    # Send some messages on O_I
    for i in range(5):
        reducer_communicator.send_message("out", Message(i, data="data"))
        mpp_server.deposit.assert_not_called()
    # Send on O_F
    reducer_communicator.send_message("final", Message(5, data="data"))
    mpp_server.deposit.assert_called_with("sibling.in2", ANY)
    mpp_server.deposit.reset_mock()

    # Pre-receive will send cached LAST message to sibling.in
    cache = reducer_communicator.pre_receive()
    assert cache[("init", None)].data == [1]
    # N.B. we don't send the [1] milestone to sibling.in due to the LAST filter, only
    # the cached message
    mpp_server.deposit.assert_called_once_with("sibling.in", ANY)
    sent_message = MPPMessage.from_bytes(mpp_server.deposit.call_args.args[1])
    assert sent_message.timestamp == 4  # The last message on O_I
    mpp_server.deposit.reset_mock()

    # Skip O_I and send on O_F
    reducer_communicator.send_message("final", Message(10, data="data"))
    mpp_server.deposit.assert_called_with("sibling.in2", ANY)
    mpp_server.deposit.reset_mock()

    # Pre-receive will first send cached LAST message to sibling.in, then receive
    # Milestone([]) and trigger:
    # - Cached LAST message on "final" to aunt.init
    # - Cached LAST LAST message on "out" to uncle.init
    # - Milestone([]) to sibling.in, sibling.in2, parent.in
    with pytest.raises(PortClosed):
        reducer_communicator.pre_receive()
    assert mpp_server.deposit.call_count == 6

    messages_per_peer_port = {}
    for call in mpp_server.deposit.call_args_list:
        msg = MPPMessage.from_bytes(call.args[1])
        messages_per_peer_port.setdefault(call.args[0], []).append(msg)

    # O_I -> last -> sibling.in
    assert len(messages_per_peer_port["sibling.in"]) == 2
    # No message was sent on O_I this reuse loop, so LAST generates an empty message:
    assert messages_per_peer_port["sibling.in"][0].timestamp == float("-inf")
    assert messages_per_peer_port["sibling.in"][0].data is None
    assert isinstance(messages_per_peer_port["sibling.in"][1].data, Milestone)
    assert messages_per_peer_port["sibling.in"][1].data.is_final_milestone()

    # Just milestones
    for peer_port in ["sibling.in2", "parent.in"]:
        assert len(messages_per_peer_port[peer_port]) == 1
        assert isinstance(messages_per_peer_port[peer_port][0].data, Milestone)
        assert messages_per_peer_port[peer_port][0].data.is_final_milestone()

    # O_I -> last last -> uncle.init
    assert len(messages_per_peer_port["uncle.init"]) == 1
    assert messages_per_peer_port["uncle.init"][0].timestamp == 4

    # O_F -> last -> aunt.init
    assert len(messages_per_peer_port["aunt.init"]) == 1
    assert messages_per_peer_port["aunt.init"][0].timestamp == 10
