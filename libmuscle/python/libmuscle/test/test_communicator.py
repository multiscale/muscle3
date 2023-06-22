import logging
from typing import List
from libmuscle.communicator import Communicator, Endpoint, Message
from libmuscle.mpp_message import ClosePort, MPPMessage
from libmuscle.port import Port

from ymmsl import Conduit, Identifier, Operator, Reference, Settings

import pytest
from unittest.mock import patch, MagicMock


def test_endpoint() -> None:
    kernel = Reference('test.kernel')
    index = [42]
    port = Identifier('out')
    slot = [2]

    endpoint = Endpoint(kernel, index, port, slot)
    assert endpoint.kernel == kernel
    assert endpoint.index == index
    assert endpoint.port == port
    assert endpoint.slot == slot

    assert str(endpoint) == 'test.kernel[42].out[2]'


def test_endpoint_instance() -> None:
    endpoint = Endpoint(Reference('test.kernel'), [42], Identifier('port'),
                        [2])
    assert endpoint.instance() == 'test.kernel[42]'

    endpoint2 = Endpoint(Reference('test.kernel'), [], Identifier('port'), [])
    assert endpoint2.instance() == 'test.kernel'

    endpoint3 = Endpoint(Reference('test.kernel'), [], Identifier('port'), [3])
    assert endpoint3.instance() == 'test.kernel'


@pytest.fixture
def communicator() -> Communicator:
    instance_id = Reference('kernel')
    communicator = Communicator(instance_id, [13], None, MagicMock())
    communicator._peer_manager = MagicMock()
    pm = communicator._peer_manager
    pm.is_connected.return_value = True

    def gpp(x) -> List[Reference]:
        if 'out' in str(x):
            return [Reference('in')]
        return [Reference('out')]

    pm.get_peer_ports = gpp

    pm.get_peer_dims.return_value = []
    pm.get_peer_locations.return_value = ['direct:test']

    def gpe(p, s) -> List[Reference]:
        endpoint = MagicMock()
        endpoint.instance.return_value = Reference('other')
        if 'out' in str(p):
            endpoint.ref.return_value = Reference('other.in[13]')
        else:
            endpoint.ref.return_value = Reference('other.out')
        return [endpoint]

    pm.get_peer_endpoints = gpe

    communicator._ports = {
            'out': Port('out', Operator.O_I, False, True, 1, []),
            'in': Port('in', Operator.S, False, True, 1, [])}
    communicator._muscle_settings_in = \
        communicator._Communicator__settings_in_port([])
    yield communicator
    communicator.shutdown()


@pytest.fixture
def communicator2() -> Communicator:
    instance_id = Reference('other')
    communicator = Communicator(instance_id, [], None, MagicMock())
    communicator._peer_manager = MagicMock()
    pm = communicator._peer_manager
    pm.is_connected.return_value = True

    def gpp(x) -> List[Reference]:
        if 'out' in str(x):
            return [Reference('in')]
        return [Reference('out')]

    pm.get_peer_ports = gpp

    pm.get_peer_dims.return_value = []
    pm.get_peer_locations.return_value = ['direct:test']

    def gpe(p, s) -> List[Reference]:
        endpoint = MagicMock()
        endpoint.instance.return_value = Reference('kernel[13]')
        if 'out' in str(p):
            endpoint.ref.return_value = Reference('kernel[13].in')
        else:
            endpoint.ref.return_value = Reference('kernel[13].out')
        return [endpoint]

    pm.get_peer_endpoints = gpe

    communicator._ports = {
            'out': Port('out', Operator.O_I, True, True, 0, [20]),
            'in': Port('in', Operator.S, True, True, 0, [20])}
    communicator._muscle_settings_in = \
        communicator._Communicator__settings_in_port([])
    yield communicator
    communicator.shutdown()


@pytest.fixture
def communicator3() -> Communicator:
    instance_id = Reference('kernel')
    communicator = Communicator(instance_id, [], None, MagicMock())
    communicator._peer_manager = MagicMock()
    pm = communicator._peer_manager
    pm.is_connected.return_value = True

    def gpp(x) -> List[Reference]:
        if 'out' in str(x):
            return [Reference('in')]
        return [Reference('out')]

    pm.get_peer_ports = gpp

    pm.get_peer_dims.return_value = []
    pm.get_peer_locations.return_value = ['direct:test']

    def gpe(p, s) -> List[Reference]:
        endpoint = MagicMock()
        endpoint.instance.return_value = Reference('other')
        if 'out' in str(p):
            endpoint.ref.return_value = Reference('other.in[13]')
        else:
            endpoint.ref.return_value = Reference('other.out[13]')
        return [endpoint]

    pm.get_peer_endpoints = gpe

    communicator._ports = {
            'out': Port('out', Operator.O_I, True, True, 0, []),
            'in': Port('in', Operator.S, True, True, 0, [])}
    yield communicator
    communicator.shutdown()


def test_create_communicator(communicator) -> None:
    assert str(communicator._kernel) == 'kernel'
    assert communicator._index == [13]
    assert len(communicator._servers) == 1
    assert communicator._clients == {}
    assert communicator._post_office._outboxes == {}


def test_get_locations(communicator) -> None:
    assert len(communicator.get_locations()) == 1
    assert communicator.get_locations()[0].startswith('tcp:')


def test_connect() -> None:
    ref = Reference

    instance_id = Reference('kernel')
    conduits = [Conduit('kernel.out', 'other.in'),
                Conduit('other.out', 'kernel.in')]
    peer_dims = {ref('other'): [1]}
    peer_locations = {ref('other'): ['direct:test']}

    with patch('libmuscle.communicator.PeerManager') as pm_init:
        communicator = Communicator(instance_id, [13], None, MagicMock())

        communicator.connect(conduits, peer_dims, peer_locations)

        pm_init.assert_called_with(instance_id, [13], conduits, peer_dims,
                                   peer_locations)

        # check inferred ports
        ports = communicator._ports
        communicator.shutdown()
        assert ports['in'].name == Identifier('in')
        assert ports['in'].operator == Operator.F_INIT
        assert ports['in']._length is None

        assert ports['out'].name == Identifier('out')
        assert ports['out'].operator == Operator.O_F
        assert ports['out']._length is None


def test_connect_vector_ports(communicator) -> None:
    ref = Reference

    communicator._declared_ports = {
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out1', 'out2[]']}

    conduits = [Conduit('other1.out', 'kernel.in'),
                Conduit('kernel.out1', 'other.in'),
                Conduit('kernel.out2', 'other3.in')]
    peer_dims = {
            ref('other1'): [20, 7],
            ref('other'): [25],
            ref('other3'): [20]}
    peer_locations = {
            ref('other'): ['direct:test'],
            ref('other1'): ['direct:test1'],
            ref('other3'): ['direct:test3']}

    communicator.connect(conduits, peer_dims, peer_locations)

    ports = communicator._ports
    assert ports['in'].name == Identifier('in')
    assert ports['in'].operator == Operator.F_INIT
    assert ports['in']._length == 7
    assert ports['in']._is_resizable is False

    assert ports['out1'].name == Identifier('out1')
    assert ports['out1'].operator == Operator.O_F
    assert ports['out1']._length is None

    assert ports['out2'].name == Identifier('out2')
    assert ports['out2'].operator == Operator.O_F
    assert ports['out2']._length == 0
    assert ports['out2']._is_resizable is True


def test_connect_multidimensional_ports(communicator) -> None:
    ref = Reference

    communicator._declared_ports = {
            Operator.F_INIT: ['in[][]']}

    conduits = [Conduit(ref('other.out'), ref('kernel.in'))]
    peer_dims = {ref('other'): [20, 7, 30]}
    peer_locations = {ref('other'): ['direct:test']}
    with pytest.raises(ValueError):
        communicator.connect(conduits, peer_dims, peer_locations)


def test_connect_inferred_ports(communicator) -> None:
    ref = Reference

    communicator._declared_ports = None

    conduits = [Conduit('other1.out', 'kernel.in'),
                Conduit('kernel.out1', 'other.in'),
                Conduit('kernel.out3', 'other2.in')]
    peer_dims = {
            ref('other1'): [20, 7],
            ref('other'): [25],
            ref('other2'): []}
    peer_locations = {
            ref('other'): ['direct:test'],
            ref('other1'): ['direct:test1'],
            ref('other2'): ['direct:test2']}

    communicator.connect(conduits, peer_dims, peer_locations)

    ports = communicator._ports
    assert ports['in'].name == Identifier('in')
    assert ports['in'].operator == Operator.F_INIT
    assert ports['in']._length == 7
    assert ports['in']._is_resizable is False

    assert ports['out1'].name == Identifier('out1')
    assert ports['out1'].operator == Operator.O_F
    assert ports['out1']._length is None

    assert ports['out3'].name == Identifier('out3')
    assert ports['out3'].operator == Operator.O_F
    assert ports['out3']._length is None


def test_send_message(communicator, message) -> None:
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._post_office._outboxes
    msg_bytes = communicator._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.timestamp == 0.0
    assert msg.next_timestamp is None
    assert msg.settings_overlay == Settings()
    assert msg.message_number == 0
    assert msg.data == b'test'


def test_send_on_disconnected_port(communicator, message) -> None:
    communicator._peer_manager.is_connected.return_value = False
    communicator.send_message('not_connected', message)


def test_send_on_invalid_port(communicator, message) -> None:
    with pytest.raises(ValueError):
        communicator.send_message('[$Invalid_id', message)


def test_send_msgpack(communicator, message2) -> None:
    communicator.send_message('out', message2)

    assert 'other.in[13]' in communicator._post_office._outboxes
    msg_bytes = communicator._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.settings_overlay == Settings()
    assert msg.message_number == 0
    assert msg.data == {'test': 17}


def test_send_message_with_slot(communicator2, message) -> None:
    communicator2.send_message('out', message, 13)

    assert 'kernel[13].in' in \
        communicator2._post_office._outboxes
    msg_bytes = communicator2._post_office._outboxes[
            'kernel[13].in']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'other.out[13]'
    assert msg.receiver == 'kernel[13].in'
    assert msg.settings_overlay == Settings()
    assert msg.message_number == 0
    assert msg.data == b'test'


def test_send_message_resizable(communicator3, message) -> None:
    with pytest.raises(RuntimeError):
        communicator3.send_message('out', message, 13)

    communicator3.get_port('out').set_length(20)
    communicator3.send_message('out', message, 13)

    assert 'other.in[13]' in communicator3._post_office._outboxes
    msg_bytes = communicator3._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel.out[13]'
    assert msg.receiver == 'other.in[13]'
    assert msg.port_length == 20


def test_send_message_with_settings(communicator, message) -> None:
    message.settings['test2'] = 'testing'
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._post_office._outboxes
    msg_bytes = communicator._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.settings_overlay.as_ordered_dict() == {'test2': 'testing'}
    assert msg.message_number == 0
    assert msg.data == b'test'


def test_send_settings(communicator, message) -> None:
    message.data = Settings()
    message.data['test1'] = 'testing'
    communicator.send_message('out', message)

    assert 'other.in[13]' in communicator._post_office._outboxes
    msg_bytes = communicator._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.settings_overlay == Settings()
    assert msg.message_number == 0
    assert msg.data == Settings({'test1': 'testing'})


def test_close_port(communicator) -> None:
    communicator.close_port('out')

    assert 'other.in[13]' in communicator._post_office._outboxes
    msg_bytes = communicator._post_office._outboxes[
            'other.in[13]']._Outbox__queue.get()
    msg = MPPMessage.from_bytes(msg_bytes)
    assert msg.sender == 'kernel[13].out'
    assert msg.receiver == 'other.in[13]'
    assert msg.timestamp == float('inf')
    assert msg.next_timestamp is None
    assert msg.settings_overlay == Settings()
    assert msg.message_number == 0
    assert isinstance(msg.data, ClosePort)


def test_receive_message(communicator, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 0, 2.0,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    msg, last_saved = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == b'test'
    assert msg.settings['test1'] == 12
    assert last_saved == 2.0


def test_receive_message_default(communicator) -> None:
    communicator._peer_manager.is_connected.return_value = False
    default_msg = Message(3.0, 4.0, 'test', Settings())
    msg, last_saved = communicator.receive_message(
            'not_connected', default=default_msg)
    assert msg.timestamp == 3.0
    assert msg.next_timestamp == 4.0
    assert msg.data == 'test'
    assert len(msg.settings) == 0
    assert last_saved == float('-inf')


def test_receive_message_no_default(communicator) -> None:
    communicator._peer_manager.is_connected.return_value = False
    with pytest.raises(RuntimeError):
        communicator.receive_message('not_connected')


def test_receive_on_invalid_port(communicator) -> None:
    with pytest.raises(ValueError):
        communicator.receive_message('@$Invalid_id')


def test_receive_msgpack(communicator, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 0, 1.0,
            {'test': 13}).encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    msg, last_saved = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == {'test': 13}
    assert last_saved == 1.0


def test_receive_with_slot(communicator2, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('kernel[13].out'), Reference('other.in[13]'),
            None, 0.0, None, Settings({'test': 'testing'}), 0, 3.0,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator2._Communicator__get_client = get_client_mock
    communicator2._profiler = MagicMock()

    msg, last_saved = communicator2.receive_message('in', 13)

    get_client_mock.assert_called_with(Reference('kernel[13]'))
    client_mock.receive.assert_called_with(Reference('other.in[13]'))
    assert msg.data == b'test'
    assert msg.settings['test'] == 'testing'
    assert last_saved == 3.0


def test_receive_message_resizable(communicator3, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel.in[13]'),
            20, 0.0, None, Settings({'test': 'testing'}), 0, 12.3,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator3._Communicator__get_client = get_client_mock
    communicator3._profiler = MagicMock()

    msg, last_saved = communicator3.receive_message('in', 13)

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel.in[13]'))
    assert msg.data == b'test'
    assert communicator3.get_port('in').get_length() == 20
    assert last_saved == 12.3


def test_receive_with_settings(communicator, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test2': 3.1}), 0, 0.1,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    msg, last_saved = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert msg.data == b'test'
    assert msg.settings['test2'] == 3.1
    assert last_saved == 0.1


def test_receive_msgpack_with_slot_and_settings(
        communicator2, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('kernel[13].out'), Reference('other.in[13]'),
            None, 0.0, 1.0, Settings({'test': 'testing'}), 0, 1.0,
            'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator2._Communicator__get_client = get_client_mock
    communicator2._profiler = MagicMock()

    msg, last_saved = communicator2.receive_message('in', 13)

    get_client_mock.assert_called_with(Reference('kernel[13]'))
    client_mock.receive.assert_called_with(Reference('other.in[13]'))
    assert msg.data == 'test'
    assert msg.settings['test'] == 'testing'
    assert last_saved == 1.0


def test_receive_settings(communicator, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 0, 1.0,
            Settings({'test': 13})).encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    msg, last_saved = communicator.receive_message('in')

    get_client_mock.assert_called_with(Reference('other'))
    client_mock.receive.assert_called_with(Reference('kernel[13].in'))
    assert isinstance(msg.data, Settings)
    assert msg.data['test'] == 13
    assert last_saved == 1.0


def test_receive_close_port(communicator, profile_data) -> None:
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings(), 0, 0.1, ClosePort()
            ).encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    msg, _ = communicator.receive_message('in')

    assert isinstance(msg.data, ClosePort)


def test_get_message(communicator, message) -> None:
    communicator.send_message('out', message, None, 2.0)
    ref_message = MPPMessage(
            Reference('kernel[13].out'), Reference('other.in[13]'),
            None, 0.0, None, Settings(), 0, 2.0, b'test').encoded()
    assert communicator._post_office.get_message(
            'other.in[13]') == ref_message


def test_port_message_counts(communicator, message) -> None:
    communicator.send_message('out', message)
    msg_counts = communicator.get_message_counts()
    assert msg_counts == {'out': [1],
                          'in': [0],
                          'muscle_settings_in': [0]}

    communicator.restore_message_counts({'out': [3],
                                         'in': [2],
                                         'muscle_settings_in': [4]})
    communicator.send_message('out', message)
    msg_counts = communicator.get_message_counts()
    assert msg_counts == {'out': [4],
                          'in': [2],
                          'muscle_settings_in': [4]}

    # empty post office
    communicator._post_office.get_message('other.in[13]')
    communicator._post_office.get_message('other.in[13]')

    with pytest.raises(RuntimeError):
        communicator.restore_message_counts({"x?invalid_port": 3})


def test_vector_port_message_counts(communicator2, message) -> None:
    msg_counts = communicator2.get_message_counts()
    assert msg_counts == {'out': [0] * 20,
                          'in': [0] * 20,
                          'muscle_settings_in': [0]}

    communicator2.send_message('out', message, 13)
    msg_counts = communicator2.get_message_counts()
    assert msg_counts == {'out': [0] * 13 + [1] + [0] * 6,
                          'in': [0] * 20,
                          'muscle_settings_in': [0]}

    communicator2.restore_message_counts({'out': list(range(20)),
                                          'in': list(range(20)),
                                          'muscle_settings_in': [4]})
    communicator2.send_message('out', message, 13)
    msg_counts = communicator2.get_message_counts()
    assert msg_counts == {'out': list(range(13)) + [14] + list(range(14, 20)),
                          'in': list(range(20)),
                          'muscle_settings_in': [4]}

    # empty post office
    communicator2._post_office.get_message('kernel[13].in')
    communicator2._post_office.get_message('kernel[13].in')


def test_port_count_validation(communicator, profile_data):
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 0, 7.6,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    communicator.receive_message('in')
    assert communicator.get_message_counts()['in'] == [1]

    with pytest.raises(RuntimeError):
        # the message received has message_number = 0 again
        communicator.receive_message('in')


def test_port_discard_error_on_resume(caplog, communicator, profile_data):
    client_mock = MagicMock()
    client_mock.receive.return_value = MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), 1, 2.3,
            b'test').encoded(), profile_data
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    communicator.restore_message_counts({'out': [0],
                                         'in': [2],
                                         'muscle_settings_in': [0]})
    for port in communicator._ports.values():
        assert port._is_resuming == [True]
        assert port.is_resuming(None)

    # In the next block, the first message with message_number=1 is discarded.
    # The RuntimeError is raised when 'receiving' the second message with
    # message_number=1
    with caplog.at_level(logging.DEBUG, 'libmuscle.communicator'):
        with pytest.raises(RuntimeError):
            communicator.receive_message('in')
        # records 0, 2 and 3 are debug logs for starting/receiving on port
        assert 'Discarding received message' in caplog.records[1].message


def test_port_discard_success_on_resume(caplog, communicator, profile_data):
    client_mock = MagicMock()
    client_mock.receive.side_effect = [(MPPMessage(
            Reference('other.out[13]'), Reference('kernel[13].in'),
            None, 0.0, None, Settings({'test1': 12}), message_number, 1.0,
            {'this is message': message_number}).encoded(), profile_data)
            for message_number in [1, 2]]
    get_client_mock = MagicMock(return_value=client_mock)
    communicator._Communicator__get_client = get_client_mock
    communicator._profiler = MagicMock()

    communicator.restore_message_counts({'out': [0],
                                         'in': [2],
                                         'muscle_settings_in': [0]})
    for port in communicator._ports.values():
        assert port._is_resuming == [True]
        assert port.is_resuming(None)

    with caplog.at_level(logging.DEBUG, 'libmuscle.communicator'):
        msg, _ = communicator.receive_message('in')
        # records 0, 2 and 3 are debug logs for starting/receiving on port
        assert 'Discarding received message' in caplog.records[1].message
    # message_number=1 should be discarded:
    assert msg.data == {'this is message': 2}
    assert communicator.get_message_counts()['in'] == [3]
