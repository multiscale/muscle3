import sys
from typing import Generator, List
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Operator, Reference

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
        communicator.receive_message.return_value = 'message'
        comm_type.return_value = communicator
        element = ComputeElement('test_element', {
            Operator.F_INIT: 'in',
            Operator.O_F: 'out'})
        yield element
        comm_type.assert_called_with(Reference('test_element'),
                                     element._configuration_store)


def test_create_compute_element(sys_argv_index):
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        ports = {
            Operator.F_INIT: 'in',
            Operator.O_F: 'out'}
        element = ComputeElement('test_element', ports)
        assert element._name == 'test_element[13][42]'
        assert element._ports == ports
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0
        assert len(element._configuration_store.overlay) == 0
        comm_type.assert_called_with(Reference('test_element[13][42]'),
                                     element._configuration_store)
        assert element._communicator == comm_type.return_value
        assert isinstance(element._configuration_store, ConfigurationStore)
        assert len(element._configuration_store.base) == 0


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


def test_send_message(compute_element):
    compute_element.send_message('out', 'message', 1)
    assert compute_element._communicator.send_message.called_with(
            'out', 'message', 1)


def test_receive_message(compute_element):
    msg = compute_element.receive_message('in', True, 1)
    assert compute_element._communicator.receive_message.called_with(
            'in', True, 1)
    assert msg == 'message'
