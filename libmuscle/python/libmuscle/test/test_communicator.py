import logging
from unittest.mock import MagicMock, Mock, patch

import pytest

from libmuscle.communicator import Communicator, Message
from libmuscle.mpp_message import ClosePort, MPPMessage
from libmuscle.peer_info import PeerInfo
from ymmsl import Conduit, Reference as Ref, Settings


@pytest.fixture
def profiler():
    return MagicMock()


@pytest.fixture(autouse=True)
def MPPServer():
    with patch('libmuscle.communicator.MPPServer') as MPPServer:
        yield MPPServer


@pytest.fixture
def mpp_server(MPPServer):
    return MPPServer.return_value


@pytest.fixture
def port_manager():
    with patch('libmuscle.communicator.PortManager') as PortManager:
        port_manager = PortManager.return_value
        port_manager.settings_in_connected.return_value = False
        yield port_manager


@pytest.fixture(autouse=True)
def MPPClient():
    with patch('libmuscle.communicator.MPPClient') as MPPClient:
        yield MPPClient


@pytest.fixture
def mpp_client(MPPClient):
    return MPPClient.return_value


@pytest.fixture
def communicator(connected_port_manager, profiler):
    return Communicator(Ref('component'), [], connected_port_manager, profiler, Mock())


@pytest.fixture
def connected_communicator(communicator):
    # These work with declared_ports and connected_port_manager in conftest.py
    conduits = [
            Conduit('peer.out', 'component.in'),
            Conduit('peer2.out_v', 'component.in_v'),
            Conduit('peer3.out_r', 'component.in_r'),
            Conduit('component.out_v', 'peer2.in'),
            Conduit('component.out_r', 'peer3.in_r'),
            Conduit('component.out', 'peer.in')]

    peer_dims = {Ref('peer'): [], Ref('peer2'): [13], Ref('peer3'): []}

    peer_locations = {
            Ref('peer'): ['tcp:peer:9001'], Ref('peer3'): ['tcp:peer3:9001']}
    peer_locations.update({
        Ref(f'peer2[{s}]'): ['tcp:peer2:9001'] for s in range(13)})

    peer_info = PeerInfo(Ref('component'), [], conduits, peer_dims, peer_locations)
    communicator.set_peer_info(peer_info)
    return communicator


def test_create_communicator(communicator, mpp_server):
    assert communicator._server == mpp_server
    pass


def test_send_message(connected_communicator, mpp_server):
    msg = Message(0.0, 1.0, 'Testing', Settings({'s0': 0, 's1': '1'}))

    connected_communicator.send_message('out_v', msg, 7, -1.0)

    mpp_server.deposit.assert_called_once()
    args = mpp_server.deposit.call_args[0]
    assert args[0] == Ref('peer2[7].in')

    encoded_msg = MPPMessage.from_bytes(args[1])
    assert encoded_msg.sender == Ref('component.out_v[7]')
    assert encoded_msg.receiver == Ref('peer2[7].in')
    assert encoded_msg.port_length is None
    assert encoded_msg.timestamp == 0.0
    assert encoded_msg.next_timestamp == 1.0
    assert len(encoded_msg.settings_overlay) == 2
    assert encoded_msg.settings_overlay['s0'] == 0
    assert encoded_msg.settings_overlay['s1'] == '1'
    assert encoded_msg.message_number == 0
    assert encoded_msg.saved_until == -1.0
    assert encoded_msg.data == 'Testing'


def test_send_message_disconnected(connected_communicator, mpp_server):
    msg = MagicMock()

    connected_communicator.send_message('not_connected', msg)

    mpp_server.deposit.assert_not_called()


def test_receive_message(connected_communicator, mpp_client):
    msg = MPPMessage(
            Ref('peer.out'), Ref('component.in'), None, 2.0, 3.0,
            Settings({'s0': '0', 's1': True}), 0, 1.0, 'Testing')

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    connected_communicator.set_receive_timeout(-1)
    recv_msg, saved_until = connected_communicator.receive_message('in')

    mpp_client.receive.assert_called_with(Ref('component.in'), None)

    assert recv_msg.timestamp == 2.0
    assert recv_msg.next_timestamp == 3.0
    assert recv_msg.data == 'Testing'
    assert len(recv_msg.settings) == 2
    assert recv_msg.settings['s0'] == '0'
    assert recv_msg.settings['s1'] is True
    assert saved_until == 1.0


def test_receive_message_vector(connected_communicator, mpp_client):
    msg = MPPMessage(
            Ref('peer2.out_v'), Ref('component.in_v'), 5, 4.0, 6.0,
            Settings({'s0': [0.0], 's1': 1.0}), 0, 3.5, 'Testing2')

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    connected_communicator.set_receive_timeout(-1)
    recv_msg, saved_until = connected_communicator.receive_message('in_v', 5)

    mpp_client.receive.assert_called_with(Ref('component.in_v[5]'), None)

    assert recv_msg.timestamp == 4.0
    assert recv_msg.next_timestamp == 6.0
    assert recv_msg.data == 'Testing2'
    assert len(recv_msg.settings) == 2
    assert recv_msg.settings['s0'] == [0.0]
    assert recv_msg.settings['s1'] == 1.0
    assert saved_until == 3.5


def test_receive_close_port(connected_communicator, mpp_client, port_manager):
    msg = MPPMessage(
            Ref('peer.out'), Ref('component.in'), None, float('inf'), None,
            Settings(), 0, 0.1, ClosePort())

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    recv_msg, saved_until = connected_communicator.receive_message('in')

    assert port_manager.get_port('in').is_open() is False


def test_receive_close_port_vector(connected_communicator, mpp_client, port_manager):
    msg = MPPMessage(
            Ref('peer2.out_v'), Ref('component.in_v'), 5, float('inf'), None,
            Settings(), 0, 3.5, ClosePort())

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    recv_msg, saved_until = connected_communicator.receive_message('in_v', 5)

    assert port_manager.get_port('in_v').is_open(5) is False


def test_port_count_validation(
        connected_communicator, mpp_client, connected_port_manager):

    msg = MPPMessage(
            Ref('peer.out'), Ref('component.in'),
            None, 0.0, None, Settings({'test1': 12}), 0, 7.6,
            b'test')

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    connected_communicator.receive_message('in')
    assert connected_port_manager.get_port('in').get_message_counts() == [1]

    with pytest.raises(RuntimeError):
        # the message received has message_number = 0 again
        connected_communicator.receive_message('in')


def test_port_discard_error_on_resume(
        caplog, connected_communicator, mpp_client, connected_port_manager):

    msg = MPPMessage(
            Ref('other.out[13]'), Ref('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 1, 2.3,
            b'test')

    mpp_client.receive.return_value = msg.encoded(), MagicMock()

    connected_port_manager.get_port('out').restore_message_counts([0])
    connected_port_manager.get_port('in').restore_message_counts([2])

    for port in ('out', 'in'):
        assert connected_port_manager.get_port(port)._is_resuming == [True]
        assert connected_port_manager.get_port(port).is_resuming(None)

    # In the next block, the first message with message_number=1 is discarded.
    # The RuntimeError is raised when 'receiving' the second message with
    # message_number=1
    with caplog.at_level(logging.DEBUG, 'libmuscle.communicator'):
        with pytest.raises(RuntimeError):
            connected_communicator.receive_message('in')

        assert any([
            'Discarding received message' in rec.message
            for rec in caplog.records])


def test_port_discard_success_on_resume(
        caplog, connected_communicator, mpp_client, connected_port_manager):

    side_effect = [(MPPMessage(
            Ref('other.out[13]'), Ref('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), message_number, 1.0,
            {'this is message': message_number}).encoded(), MagicMock())
            for message_number in [1, 2]]

    mpp_client.receive.side_effect = side_effect

    connected_port_manager.get_port('out').restore_message_counts([0])
    connected_port_manager.get_port('in').restore_message_counts([2])

    for port in ('out', 'in'):
        assert connected_port_manager.get_port(port)._is_resuming == [True]
        assert connected_port_manager.get_port(port).is_resuming(None)

    with caplog.at_level(logging.DEBUG, 'libmuscle.communicator'):
        msg, _ = connected_communicator.receive_message('in')
        assert any([
            'Discarding received message' in rec.message
            for rec in caplog.records])

    # message_number=1 should have been discarded:
    assert msg.data == {'this is message': 2}
    assert connected_communicator._port_manager.get_port(
            'in').get_message_counts() == [3]


def test_shutdown(
        connected_communicator, mpp_client, connected_port_manager, mpp_server):

    msg = MPPMessage(
            Ref('peer.out'), Ref('component.in'), None, float('inf'), None,
            Settings(), 0, 0.0, ClosePort())

    messages = {Ref('component.in'): msg}

    port_sender = {
            'in_v': 'peer2[x].out_v',
            'in_r': 'peer3.out_r[x]'}

    for port_name, snd in port_sender.items():
        port = connected_port_manager.get_port(port_name)
        for slot in range(port.get_length()):
            sender = Ref(snd.replace('x', str(slot)))
            receiver = Ref(f'component.{port_name}[{slot}]')

            messages[receiver] = MPPMessage(
                    sender, receiver, slot, float('inf'), None,
                    Settings(), 0, 3.5, ClosePort())

    def receive(receiver, timeout_handler):
        return messages[receiver].encoded(), MagicMock()

    mpp_client.receive = receive

    connected_communicator.shutdown()

    expected_receivers = (
            {Ref('peer.in')} |
            {
                Ref(f'peer2[{slot}].in')
                for slot in range(
                    connected_port_manager.get_port('out_v').get_length())} |
            {
                Ref(f'peer3.in[{slot}]')
                for slot in range(
                    connected_port_manager.get_port('out_r').get_length())})

    for call in mpp_server.deposit.call_args_list:
        assert call[0][0] in expected_receivers
        msg = MPPMessage.from_bytes(call[0][1])
        assert isinstance(msg.data, ClosePort)
        expected_receivers.remove(call[0][0])

    assert not expected_receivers
