import sys
from typing import Generator, List
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Conduit, Operator, Reference

from libmuscle.communicator import _ClosePort, Message
from libmuscle.compute_element import ComputeElement
from libmuscle.configuration import Configuration
from libmuscle.configuration_store import ConfigurationStore


@pytest.fixture
def sys_argv_index() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-index=13,42']
    yield
    sys.argv = old_argv


@pytest.fixture
def compute_element():
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        communicator = MagicMock()
        config = Configuration()
        config['test1'] = 12
        msg = Message(0.0, 1.0, 'message', config)
        communicator.receive_message.return_value = msg
        comm_type.return_value = communicator
        element = ComputeElement('test_element', {
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.O_F: ['out']})
        element._f_init_cache = dict()
        element._f_init_cache[('in', None)] = msg
        yield element


@pytest.fixture
def compute_element2():
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        element = ComputeElement('test_element', {
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out']})
        yield element


def test_create_compute_element(sys_argv_index):
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        ports = {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']}
        element = ComputeElement('test_element', ports)
        assert element._name == Reference('test_element')
        assert element._index == [13, 42]
        assert element._declared_ports == ports
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0
        assert len(element._configuration_store.overlay) == 0
        comm_type.assert_called_with(Reference('test_element'), [13, 42],
                                     ports)
        assert element._communicator == comm_type.return_value
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0


def test_get_parameter_value(compute_element):
    ref = Reference
    config = Configuration()
    config[ref('test1')] = 'test'
    config[ref('test2')] = 12
    config[ref('test3')] = 27.1
    config[ref('test4')] = True
    config[ref('test5')] = [2.3, 5.6]
    config[ref('test6')] = [[1.0, 2.0], [3.0, 4.0]]
    compute_element._configuration_store.base = config

    assert compute_element.get_parameter_value('test1') == 'test'
    assert compute_element.get_parameter_value('test2') == 12
    assert compute_element.get_parameter_value('test3') == 27.1
    assert compute_element.get_parameter_value('test4') is True
    assert compute_element.get_parameter_value('test5') == [2.3, 5.6]
    assert compute_element.get_parameter_value('test6') == [
            [1.0, 2.0], [3.0, 4.0]]

    assert compute_element.get_parameter_value('test1', 'str') == 'test'
    assert compute_element.get_parameter_value('test2', 'int') == 12
    assert compute_element.get_parameter_value('test3', 'float') == 27.1
    assert compute_element.get_parameter_value('test4', 'bool') is True
    assert (compute_element.get_parameter_value('test5', '[float]') ==
            [2.3, 5.6])
    assert (compute_element.get_parameter_value('test6', '[[float]]') ==
            [[1.0, 2.0], [3.0, 4.0]])

    with pytest.raises(KeyError):
        compute_element.get_parameter_value('testx')

    with pytest.raises(TypeError):
        compute_element.get_parameter_value('test1', 'int')
    with pytest.raises(TypeError):
        compute_element.get_parameter_value('test6', '[float]')
    with pytest.raises(TypeError):
        compute_element.get_parameter_value('test5', '[[float]]')
    with pytest.raises(ValueError):
        compute_element.get_parameter_value('test2', 'nonexistenttype')


def test_list_ports(compute_element):
    ports = compute_element.list_ports()
    assert compute_element._communicator.list_ports.called_with()
    assert ports == compute_element._communicator.list_ports.return_value


def test_is_vector_port(compute_element):
    compute_element._communicator.get_port.return_value.is_vector = MagicMock(
            return_value=True)
    is_vector = compute_element.is_vector_port('out_port')
    assert is_vector is True
    assert compute_element._communicator.get_port.called_with('out_port')


def test_send_message(compute_element, message):
    compute_element.send_message('out', message, 1)
    assert compute_element._communicator.send_message.called_with(
            'out', message, 1)


def test_send_message_invalid_port(compute_element, message):
    compute_element._communicator.port_exists.return_value = False
    with pytest.raises(ValueError):
        compute_element.send_message('does_not_exist', message, 1)


def test_receive_message(compute_element):
    compute_element._communicator.get_port.return_value = MagicMock(
            operator=Operator.F_INIT)
    msg = compute_element.receive_message('in')
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert compute_element._communicator.receive_message.called_with(
            'in', None)
    assert msg.data == 'message'

    with pytest.raises(RuntimeError):
        compute_element.receive_message('in')


def test_receive_message_default(compute_element):
    compute_element._communicator.port_exists.return_value = True
    port = compute_element._communicator.get_port.return_value
    port.operator = Operator.F_INIT
    port.is_connected.return_value = False
    compute_element.receive_message('not_connected', 1, 'testing')
    assert compute_element._communicator.receive_message.called_with(
            'not_connected', 1, 'testing')
    with pytest.raises(RuntimeError):
        compute_element.receive_message('not_connected', 1)


def test_receive_message_invalid_port(compute_element):
    compute_element._communicator.port_exists.return_value = False
    with pytest.raises(ValueError):
        compute_element.receive_message('does_not_exist', 1)


def test_receive_message_with_parameters(compute_element):
    msg = compute_element.receive_message_with_parameters('in', 1)
    assert (compute_element._communicator.receive_message
            .called_with('in', 1))
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.data == 'message'
    assert msg.configuration['test1'] == 12


def test_receive_message_with_parameters_default(compute_element):
    compute_element.receive_message_with_parameters('not_connected', 1,
                                                    'testing')
    assert compute_element._communicator.receive_message.called_with(
            'not_connected', 1, 'testing')


def test_receive_parallel_universe(compute_element) -> None:
    compute_element._configuration_store.overlay['test2'] = 'test'
    with pytest.raises(RuntimeError):
        compute_element.receive_message('in')


def test_reuse_instance_receive_overlay(compute_element):
    compute_element._configuration_store.overlay = Configuration()
    test_base_config = Configuration()
    test_base_config['test1'] = 24
    test_base_config['test2'] = [1.3, 2.0]
    test_overlay = Configuration()
    test_overlay['test2'] = 'abc'
    recv = compute_element._communicator.receive_message
    recv.return_value = Message(0.0, None, test_overlay, test_base_config)
    compute_element.reuse_instance()
    assert compute_element._communicator.receive_message.called_with(
        'muscle_parameters_in')
    assert len(compute_element._configuration_store.overlay) == 2
    assert compute_element._configuration_store.overlay['test1'] == 24
    assert compute_element._configuration_store.overlay['test2'] == 'abc'


def test_reuse_instance_closed_port(compute_element):
    def receive_message(port_name, slot=None, default=None):
        if port_name == 'muscle_parameters_in':
            return Message(0.0, None, Configuration(), Configuration())
        elif port_name == 'in':
            return Message(0.0, None, _ClosePort(), Configuration())
        assert False    # pragma: no cover

    def get_port(port_name):
        port = MagicMock()
        port.is_vector.return_value = False
        if port_name == 'not_connected':
            port.is_connected.return_value = False
        else:
            port.is_connected.return_value = True
        return port

    compute_element._communicator.receive_message = receive_message
    compute_element._communicator.list_ports.return_value = {
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.O_F: ['out']}
    compute_element._communicator.get_port = get_port

    do_reuse = compute_element.reuse_instance()
    assert do_reuse is False


def test_reuse_instance_vector_port(compute_element2):
    def receive_message(port_name, slot=None, default=None):
        if port_name == 'muscle_parameters_in':
            return Message(0.0, None, Configuration(), Configuration())
        elif port_name == 'in':
            data = 'test {}'.format(slot)
            return Message(0.0, None, data, Configuration())
        assert False    # pragma: no cover

    compute_element2._communicator.receive_message = receive_message
    compute_element2._communicator.list_ports.return_value = {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']}

    port = MagicMock()
    port.is_vector.return_value = True
    port.is_connected.return_value = True
    port.get_length.return_value = 10
    compute_element2._communicator.get_port.return_value = port

    do_reuse = compute_element2.reuse_instance()
    assert do_reuse is True

    msg = compute_element2.receive_message('in', 5)
    assert msg.timestamp == 0.0
    assert msg.next_timestamp is None
    assert msg.data == 'test 5'


def test_reuse_instance_no_f_init_ports(compute_element):
    compute_element._communicator.receive_message.return_value = Message(
            0.0, None, Configuration(), Configuration())
    compute_element._communicator.list_ports.return_value = {}
    compute_element._communicator.parameters_in_connected.return_value = False
    do_reuse = compute_element.reuse_instance()
    assert do_reuse is True
    do_reuse = compute_element.reuse_instance()
    assert do_reuse is False


def test_reuse_instance_miswired(compute_element):
    with pytest.raises(RuntimeError):
        compute_element.reuse_instance()
