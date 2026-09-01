from typing import Union
from unittest.mock import MagicMock, patch

import pytest
from ymmsl.v0_2 import Conduit, ConduitFilter, Operator, Port, Settings
from ymmsl.v0_2 import Identifier as Id
from ymmsl.v0_2 import Reference as Ref

from libmuscle.communicator import Communicator, PortClosed
from libmuscle.mpp_message import Milestone, MPPMessage
from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager
from libmuscle.timeline_manager import IterationCount


@pytest.fixture
def mpp_client():
    with patch("libmuscle.communicator.MPPClient") as MPPClient:
        yield MPPClient.return_value


@pytest.fixture(params=["repeat", "pad"])
def repeat_filter(request):
    return request.param


@pytest.fixture()
def repeater_communicator(repeat_filter, mpp_client):
    port_manager = PortManager([], None)
    communicator = Communicator(
        Ref("component"), [], port_manager, MagicMock(), MagicMock()
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
    twicerepeated_messages = [[], Milestone([])]
    repeated_messages = [[0], [1], [2], Milestone([])]
    unfiltered_messages = [
        [0, 0],
        [0, 1],
        Milestone([0]),
        # parent is allowed to send 0 messages on its O_I port in an iteration
        Milestone([1]),
        [2, 0],
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
    assert cache[("unfiltered", None)].data == [0, 0]
    assert cache[("repeated", None)].data == [0]
    assert cache[("twicerepeated", None)].data == []

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [0, 1]
    assert cache[("repeated", None)].data == (None if is_padded else [0])
    assert cache[("twicerepeated", None)].data == (None if is_padded else [])

    cache = repeater_communicator.pre_receive()
    assert cache[("unfiltered", None)].data == [2, 0]
    assert cache[("repeated", None)].data == [2]
    assert cache[("twicerepeated", None)].data == (None if is_padded else [])

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
