import sys
from typing import Generator, List
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Conduit, Operator, Reference

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
        communicator.receive_message.return_value = (
                'message', config)
        comm_type.return_value = communicator
        element = ComputeElement('test_element', {
            Operator.F_INIT: ['in', 'not_connected'],
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
        assert element._ports == ports
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0
        assert len(element._configuration_store.overlay) == 0
        comm_type.assert_called_with(Reference('test_element'), [13, 42])
        assert element._communicator == comm_type.return_value
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0
        ref_ports = {
                'in': Operator.F_INIT,
                'out': Operator.O_F}
        assert element._port_operators == ref_ports


def test_create_compute_element_inferred_ports(sys_argv_index):
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        element = ComputeElement('test_element')
        assert element._name == Reference('test_element')
        assert element._index == [13, 42]
        assert element._ports is None

        with pytest.raises(RuntimeError):
            element.get_ports()

        conduits = [
                Conduit(Reference('other.out'), Reference('test_element.in')),
                Conduit(Reference('test_element.out'), Reference('other2.in'))]
        peer_dims = MagicMock()
        peer_locations = MagicMock()
        element._connect(conduits, peer_dims, peer_locations)
        element._communicator.connect.assert_called_with(
                conduits, peer_dims, peer_locations)

        ports = {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']}
        assert element._ports == ports
        assert element.get_ports() == ports

        port_ops = {
                'in': Operator.F_INIT,
                'out': Operator.O_F}
        assert element._port_operators == port_ops


def test_get_parameter_value(compute_element):
    config = Configuration()
    config['test1'] = 'test'
    config['test2'] = 12
    config['test3'] = 27.1
    config['test4'] = True
    config['test5'] = [2.3, 5.6]
    config['test6'] = [[1.0, 2.0], [3.0, 4.0]]
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


def test_send_message(compute_element, message):
    compute_element.send_message('out', message, 1)
    assert compute_element._communicator.send_message.called_with(
            'out', message, 1)


def test_send_message_invalid_port(compute_element, message):
    with pytest.raises(ValueError):
        compute_element.send_message('does_not_exist', message, 1)


def test_receive_message(compute_element):
    msg = compute_element.receive_message('in', True, 1)
    assert compute_element._communicator.receive_message.called_with(
            'in', True, 1)
    assert msg == 'message'


def test_receive_message_default(compute_element):
    compute_element.receive_message('not_connected', True, 1, 'testing')
    assert compute_element._communicator.receive_message.called_with(
            'not_connected', True, 1, 'testing')


def test_receive_message_invalid_port(compute_element):
    with pytest.raises(ValueError):
        compute_element.receive_message('does_not_exist', True, 1)


def test_receive_message_with_parameters(compute_element):
    msg, config = compute_element.receive_message_with_parameters(
            'in', True, 1)
    assert (compute_element._communicator.receive_message_with_parameters
            .called_with('in', True, 1))
    assert msg == 'message'
    assert config['test1'] == 12


def test_receive_message_with_parameters_default(compute_element):
    compute_element.receive_message_with_parameters('not_connected', True, 1,
                                                    'testing')
    assert compute_element._communicator.receive_message.called_with(
            'not_connected', True, 1, 'testing')


def test_receive_parallel_universe(compute_element) -> None:
    compute_element._configuration_store.overlay['test2'] = 'test'
    with pytest.raises(RuntimeError):
        compute_element.receive_message('in', True)


def test_init_instance(compute_element):
    compute_element._configuration_store.overlay = Configuration()
    test_base_config = Configuration()
    test_base_config['test1'] = 24
    test_base_config['test2'] = [1.3, 2.0]
    test_overlay = Configuration()
    test_overlay['test2'] = 'abc'
    recv = compute_element._communicator.receive_message
    recv.return_value = (test_overlay, test_base_config)
    compute_element.init_instance()
    assert compute_element._communicator.receive_message.called_with(
        'muscle_parameters_in', True)
    assert len(compute_element._configuration_store.overlay) == 2
    assert compute_element._configuration_store.overlay['test1'] == 24
    assert compute_element._configuration_store.overlay['test2'] == 'abc'


def test_init_instance_miswired(compute_element):
    with pytest.raises(RuntimeError):
        compute_element.init_instance()
