from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Reference

from libmuscle.compute_element import ComputeElement


@pytest.fixture
def compute_element():
    with patch('libmuscle.compute_element.Communicator') as comm_type:
        communicator = MagicMock()
        communicator.receive_message.return_value = 'message'
        comm_type.return_value = communicator
        yield ComputeElement(Reference('test_element'))
        comm_type.assert_called_with(Reference('test_element'))


def test_send_message(compute_element):
    compute_element.send_message('test_port', 'message', 1)
    assert compute_element._communicator.send_message.called_with(
            'test_port', 'message', 1)


def test_receive_message(compute_element):
    msg = compute_element.receive_message('test_port', True, 1)
    assert compute_element._communicator.receive_message.called_with(
            'test_port', True, 1)
    assert msg == 'message'
