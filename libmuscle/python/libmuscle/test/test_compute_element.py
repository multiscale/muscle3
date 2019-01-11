import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Operator, Reference

from libmuscle.compute_element import ComputeElement


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
        yield ComputeElement('test_element', {
            Operator.F_INIT: 'in',
            Operator.O_F: 'out'})
        comm_type.assert_called_with(Reference('test_element'))


def test_create_compute_element(sys_argv_index):
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        ports = {
            Operator.F_INIT: 'in',
            Operator.O_F: 'out'}
        element = ComputeElement('test_element', ports)
        assert element._name == 'test_element[13][42]'
        comm_type.assert_called_with(Reference('test_element[13][42]'))
        assert element._communicator == comm_type.return_value
        assert element._ports == ports


def test_send_message(compute_element):
    compute_element.send_message('out', 'message', 1)
    assert compute_element._communicator.send_message.called_with(
            'out', 'message', 1)


def test_receive_message(compute_element):
    msg = compute_element.receive_message('in', True, 1)
    assert compute_element._communicator.receive_message.called_with(
            'in', True, 1)
    assert msg == 'message'
