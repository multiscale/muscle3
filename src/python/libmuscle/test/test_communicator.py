import logging
from unittest.mock import MagicMock, Mock, patch

import pytest
from ymmsl.v0_2 import Conduit, Settings
from ymmsl.v0_2 import Reference as Ref

from libmuscle.communicator import Communicator, Message, PortClosed
from libmuscle.mpp_message import Milestone, MPPMessage
from libmuscle.peer_info import PeerInfo


@pytest.fixture
def profiler():
    return MagicMock()


@pytest.fixture(autouse=True)
def MPPServer():
    with patch("libmuscle.communicator.MPPServer") as MPPServer:
        yield MPPServer


@pytest.fixture
def mpp_server(MPPServer):
    return MPPServer.return_value


@pytest.fixture
def port_manager():
    with patch("libmuscle.communicator.PortManager") as PortManager:
        port_manager = PortManager.return_value
        port_manager.settings_in_connected.return_value = False
        yield port_manager


@pytest.fixture(autouse=True)
def MPPClient():
    with patch("libmuscle.communicator.MPPClient") as MPPClient:
        yield MPPClient


@pytest.fixture
def mpp_client(MPPClient):
    return MPPClient.return_value


@pytest.fixture
def timeline_manager():
    with patch("libmuscle.communicator.TimelineManager") as MockTimelineManager:
        MockTimelineManager.return_value.start_reuse_iteration.return_value = None
        yield MockTimelineManager


@pytest.fixture
def communicator(connected_port_manager, profiler, timeline_manager):
    return Communicator(Ref("component"), [], connected_port_manager, profiler, Mock())


@pytest.fixture
def connected_communicator(communicator):
    # These work with declared_ports and connected_port_manager in conftest.py
    conduits = [
        Conduit("peer.out", "component.in"),
        Conduit("peer2.out_v", "component.in_v"),
        Conduit("peer3.out_r", "component.in_r"),
        Conduit("component.out_v", "peer2.in"),
        Conduit("component.out_r", "peer3.in_r"),
        Conduit("component.out", "peer.in"),
        Conduit("qmc.out", "component.muscle_settings_in"),
    ]

    peer_dims = {Ref("peer"): [], Ref("peer2"): [13], Ref("peer3"): [], Ref("qmc"): []}

    peer_locations = {
        Ref("peer"): ["tcp:peer:9001"],
        Ref("peer3"): ["tcp:peer3:9001"],
        Ref("qmc"): ["tcp:qmc:9001"],
    }
    peer_locations.update({Ref(f"peer2[{s}]"): ["tcp:peer2:9001"] for s in range(13)})

    peer_info = PeerInfo(Ref("component"), [], conduits, peer_dims, peer_locations, [])
    communicator.set_peer_info(peer_info)
    return communicator


def mock_mpp_receive(
    sender="snd",  # Not correct, but unused in receive_message
    receiver="rcv",  # Not correct, but unused in receive_message
    port_length=None,
    timestamp=0.0,
    next_timestamp=None,
    settings_overlay=None,
    message_number=0,
    data=None,
    iteration=None,
):
    """Helper method for mocking return values for mpp_client.receive."""
    return MPPMessage(
        Ref(str(sender)),
        Ref(str(receiver)),
        port_length,
        timestamp,
        next_timestamp,
        Settings() if settings_overlay is None else settings_overlay,
        message_number,
        data,
        iteration or [],
    ).encoded(), MagicMock()


def test_create_communicator(communicator, mpp_server):
    assert communicator._server == mpp_server
    pass


def test_set_peer_info_creates_timeline_manager(
    communicator, connected_port_manager, timeline_manager
):
    peer_info = MagicMock()

    communicator.set_peer_info(peer_info)

    assert communicator._peer_info == peer_info
    timeline_manager.assert_called_once_with(connected_port_manager)
    assert communicator._timeline_manager == timeline_manager.return_value


def test_send_message(connected_communicator, mpp_server, timeline_manager):
    timeline_manager.return_value.check_send_message.return_value = [2, 0]
    msg = Message(0.0, 1.0, "Testing", Settings({"s0": 0, "s1": "1"}))

    connected_communicator.send_message("out_v", msg, 7)

    mpp_server.deposit.assert_called_once()
    args = mpp_server.deposit.call_args[0]
    assert args[0] == Ref("peer2[7].in")

    encoded_msg = MPPMessage.from_bytes(args[1])
    assert encoded_msg.sender == Ref("component.out_v[7]")
    assert encoded_msg.receiver == Ref("peer2[7].in")
    assert encoded_msg.port_length is None
    assert encoded_msg.timestamp == 0.0
    assert encoded_msg.next_timestamp == 1.0
    assert len(encoded_msg.settings_overlay) == 2
    assert encoded_msg.settings_overlay["s0"] == 0
    assert encoded_msg.settings_overlay["s1"] == "1"
    assert encoded_msg.message_number == 0
    assert encoded_msg.data == "Testing"
    assert encoded_msg.iteration == [2, 0]
    timeline_manager.return_value.check_send_message.assert_called_with("out_v", 7)


def test_send_message_disconnected(connected_communicator, mpp_server):
    msg = MagicMock()

    connected_communicator.send_message("not_connected", msg)

    mpp_server.deposit.assert_not_called()


def test_receive_s_message(connected_communicator, mpp_client):
    mpp_client.receive.return_value = mock_mpp_receive(
        Ref("peer.out"),
        Ref("component.in"),
        None,
        2.0,
        3.0,
        Settings({"s0": "0", "s1": True}),
        0,
        "Testing",
        [0],
    )

    connected_communicator.set_receive_timeout(-1)
    recv_msg = connected_communicator.receive_s_message("in")

    mpp_client.receive.assert_called_with(Ref("component.in"), None)

    assert recv_msg.timestamp == 2.0
    assert recv_msg.next_timestamp == 3.0
    assert recv_msg.data == "Testing"
    assert len(recv_msg.settings) == 2
    assert recv_msg.settings["s0"] == "0"
    assert recv_msg.settings["s1"] is True


def test_receive_message_vector(connected_communicator, mpp_client):
    mpp_client.receive.return_value = mock_mpp_receive(
        Ref("peer2.out_v"),
        Ref("component.in_v"),
        5,
        4.0,
        6.0,
        Settings({"s0": [0.0], "s1": 1.0}),
        0,
        "Testing2",
        [0],
    )

    connected_communicator.set_receive_timeout(-1)
    recv_msg = connected_communicator.receive_s_message("in_v", 5)

    mpp_client.receive.assert_called_with(Ref("component.in_v[5]"), None)

    assert recv_msg.timestamp == 4.0
    assert recv_msg.next_timestamp == 6.0
    assert recv_msg.data == "Testing2"
    assert len(recv_msg.settings) == 2
    assert recv_msg.settings["s0"] == [0.0]
    assert recv_msg.settings["s1"] == 1.0


def test_receive_root_milestone(connected_communicator, mpp_client, port_manager):
    mpp_client.receive.return_value = mock_mpp_receive(data=Milestone([]))

    with pytest.raises(PortClosed):
        connected_communicator.receive_s_message("in")

    assert port_manager.get_port("in").is_open() is False


def test_receive_root_milestone_vector(
    connected_communicator, mpp_client, port_manager
):
    mpp_client.receive.return_value = mock_mpp_receive(data=Milestone([]))

    with pytest.raises(PortClosed):
        connected_communicator.receive_s_message("in_v", 5)

    assert port_manager.get_port("in_v").is_open(5) is False


def test_pre_receive_f_init(connected_communicator, mpp_client):
    mpp_client.receive.return_value = mock_mpp_receive(data="test")

    cache = connected_communicator.pre_receive_f_init()
    assert len(cache) == 1
    assert cache[("in", None)].data == "test"


def test_pre_receive_f_init_with_settings(
    connected_communicator, connected_port_manager, mpp_client
):
    mpp_client.receive.return_value = mock_mpp_receive(data=Settings({"a": True}))
    connected_port_manager.settings_in_connected.return_value = True

    cache = connected_communicator.pre_receive_f_init()
    assert cache.keys() == {("in", None), ("muscle_settings_in", None)}
    for msg in cache.values():
        assert msg.data == Settings({"a": True})


def test_pre_receive_close_port(connected_communicator, mpp_client):
    mpp_client.receive.return_value = mock_mpp_receive(data=Milestone([]))

    with pytest.raises(PortClosed):
        connected_communicator.pre_receive_f_init()


def test_pre_receive_vector(connected_communicator, mock_ports, mpp_client):
    mpp_client.receive.return_value = mock_mpp_receive(data="test")
    mock_ports["in"]._is_resizable = True
    mock_ports["in"].set_length(4)

    cache = connected_communicator.pre_receive_f_init()
    assert cache.keys() == {("in", slot) for slot in range(4)}


def test_pre_receive_broadcast_milestone(
    connected_communicator, mock_ports, mpp_client, mpp_server
):
    mpp_client.receive.side_effect = [
        (mock_mpp_receive(data=Milestone([1]), iteration=[1])),
        (mock_mpp_receive(data="test data", iteration=[2, 0])),
    ]

    cache = connected_communicator.pre_receive_f_init()
    assert cache.keys() == {("in", None)}
    assert cache[("in", None)].data == "test data"
    # Expect a milestone broadcasted to all O_I and O_F ports
    num_oi = mock_ports["out_v"].get_length() + mock_ports["out_r"].get_length()
    num_of = 1  # out is a scalar port
    assert mpp_server.deposit.call_count == num_of + num_oi
    for call in mpp_server.deposit.call_args_list:
        msg = MPPMessage.from_bytes(call[0][1])
        assert isinstance(msg.data, Milestone)
        assert msg.data.iteration == [1]


def test_pre_receive_different_milestones(
    connected_communicator, connected_port_manager, mpp_client
):
    connected_port_manager.settings_in_connected.return_value = True
    # One of these is received on "in", the other on "muscle_settings_in":
    mpp_client.receive.side_effect = [
        (mock_mpp_receive(data=Milestone([1]), iteration=[1])),
        (mock_mpp_receive(data=Milestone([2]), iteration=[2])),
    ]

    with pytest.raises(RuntimeError, match="different iterations"):
        connected_communicator.pre_receive_f_init()


def test_pre_receive_some_port_closed(
    connected_communicator, connected_port_manager, mpp_client
):
    connected_port_manager.settings_in_connected.return_value = True
    # One of these is received on "in", the other on "muscle_settings_in":
    mpp_client.receive.side_effect = [
        (mock_mpp_receive(data=Milestone([1]), iteration=[1])),
        (mock_mpp_receive(data=Milestone([]), iteration=[])),
    ]

    with pytest.raises(RuntimeError, match="unexpectedly closed"):
        connected_communicator.pre_receive_f_init()


def test_port_count_validation(
    connected_communicator, mpp_client, connected_port_manager
):
    mpp_client.receive.return_value = mock_mpp_receive(
        Ref("peer.out"),
        Ref("component.in"),
        None,
        0.0,
        None,
        Settings({"test1": 12}),
        0,
        b"test",
        [0],
    )

    connected_communicator.receive_s_message("in")
    assert connected_port_manager.get_port("in").get_message_counts() == [1]

    with pytest.raises(RuntimeError):
        # the message received has message_number = 0 again
        connected_communicator.receive_s_message("in")


def test_port_discard_error_on_resume(
    caplog, connected_communicator, mpp_client, connected_port_manager
):
    mpp_client.receive.return_value = mock_mpp_receive(
        Ref("other.out[13]"),
        Ref("kernel[13].in"),
        None,
        0.0,
        None,
        Settings({"test1": 12}),
        1,
        b"test",
        [],
    )

    connected_port_manager.get_port("out").restore_message_counts([0])
    connected_port_manager.get_port("in").restore_message_counts([2])

    for port in ("out", "in"):
        assert connected_port_manager.get_port(port)._is_resuming == [True]
        assert connected_port_manager.get_port(port).is_resuming(None)

    # In the next block, the first message with message_number=1 is discarded.
    # The RuntimeError is raised when 'receiving' the second message with
    # message_number=1
    with caplog.at_level(logging.DEBUG, "libmuscle.communicator"):
        with pytest.raises(RuntimeError):
            connected_communicator.receive_s_message("in")

        assert any(
            ["Discarding received message" in rec.message for rec in caplog.records]
        )


def test_port_discard_success_on_resume(
    caplog, connected_communicator, mpp_client, connected_port_manager
):

    mpp_client.receive.side_effect = [
        mock_mpp_receive(
            Ref("other.out[13]"),
            Ref("kernel[13].in"),
            None,
            0.0,
            None,
            Settings({"test1": 12}),
            message_number,
            {"this is message": message_number},
            [0],
        )
        for message_number in [1, 2]
    ]

    connected_port_manager.get_port("out").restore_message_counts([0])
    connected_port_manager.get_port("in").restore_message_counts([2])

    for port in ("out", "in"):
        assert connected_port_manager.get_port(port)._is_resuming == [True]
        assert connected_port_manager.get_port(port).is_resuming(None)

    with caplog.at_level(logging.DEBUG, "libmuscle.communicator"):
        msg = connected_communicator.receive_s_message("in")
        assert any(
            ["Discarding received message" in rec.message for rec in caplog.records]
        )

    # message_number=1 should have been discarded:
    assert msg.data == {"this is message": 2}
    assert connected_communicator._port_manager.get_port("in").get_message_counts() == [
        3
    ]


def test_shutdown(
    connected_communicator, mpp_client, connected_port_manager, mpp_server
):

    msg = MPPMessage(
        Ref("peer.out"),
        Ref("component.in"),
        None,
        float("inf"),
        None,
        Settings(),
        0,
        Milestone([]),
        [],
    )

    messages = {Ref("component.in"): msg}

    port_sender = {"in_v": "peer2[x].out_v", "in_r": "peer3.out_r[x]"}

    for port_name, snd in port_sender.items():
        port = connected_port_manager.get_port(port_name)
        for slot in range(port.get_length()):
            sender = Ref(snd.replace("x", str(slot)))
            receiver = Ref(f"component.{port_name}[{slot}]")

            messages[receiver] = MPPMessage(
                sender,
                receiver,
                slot,
                float("inf"),
                None,
                Settings(),
                0,
                Milestone([]),
                [],
            )

    def receive(receiver, timeout_handler):
        return messages[receiver].encoded(), MagicMock()

    mpp_client.receive = receive

    connected_communicator.shutdown()

    expected_receivers = (
        {Ref("peer.in")}
        | {
            Ref(f"peer2[{slot}].in")
            for slot in range(connected_port_manager.get_port("out_v").get_length())
        }
        | {
            Ref(f"peer3.in[{slot}]")
            for slot in range(connected_port_manager.get_port("out_r").get_length())
        }
    )

    for call in mpp_server.deposit.call_args_list:
        assert call[0][0] in expected_receivers
        msg = MPPMessage.from_bytes(call[0][1])
        assert isinstance(msg.data, Milestone)
        expected_receivers.remove(call[0][0])

    assert not expected_receivers


def test_send_milestone_at_reuse(
    connected_communicator, timeline_manager, mock_ports, mpp_server, mpp_client
):
    mpp_client.receive.return_value = mock_mpp_receive(data=None, iteration=[1, 3])
    timeline_manager().start_reuse_iteration.return_value = [1, 2]

    connected_communicator.pre_receive_f_init()

    timeline_manager().start_reuse_iteration.assert_called_once()
    # Expect a milestone broadcasted to all O_I ports
    num_expected = mock_ports["out_v"].get_length() + mock_ports["out_r"].get_length()
    assert mpp_server.deposit.call_count == num_expected
    for call in mpp_server.deposit.call_args_list:
        assert str(call[0][0]).startswith(("peer2", "peer3"))
        msg = MPPMessage.from_bytes(call[0][1])
        assert isinstance(msg.data, Milestone)
        assert msg.data.iteration == [1, 2]
