from libmuscle import Muscle3

import pytest
from ymmsl import Operator, Port, Reference

from unittest.mock import MagicMock, patch
import sys
from typing import Generator


@pytest.fixture
def sys_argv_manager() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv


@pytest.fixture
def log_file_in_tmpdir(tmpdir) -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-log-file={}'.format(tmpdir)]
    yield None
    sys.argv = old_argv


def test_extract_manager_location(sys_argv_manager) -> None:
    assert (Muscle3._Muscle3__extract_manager_location() ==
            'localhost:9000')


def test_muscle_init_no_manager(log_file_in_tmpdir) -> None:
    muscle = Muscle3()
    assert muscle._Muscle3__manager is None


def test_muscle_init_manager(log_file_in_tmpdir, sys_argv_manager) -> None:
    with patch('libmuscle.muscle3.MMPClient') as mock_client:
        Muscle3()
        mock_client.assert_called_once_with('localhost:9000')


def test_register(log_file_in_tmpdir) -> None:
    muscle = Muscle3()
    manager_client = MagicMock()
    manager_client.request_peers = MagicMock(return_value=(1, 2, 3))
    muscle._Muscle3__manager = manager_client

    element = MagicMock()
    element._name = Reference('test_model')
    element._index = []
    element._declared_ports = {
            Operator.F_INIT: ['receive_init'],
            Operator.O_F: ['send_output']}
    muscle.register([element])

    args = manager_client.register_instance.call_args[0]
    assert args[0] == Reference('test_model')
    assert args[1] == element._communicator.get_locations.return_value
    ports = sorted(args[2], key=lambda port: port.name)
    assert ports[0].name == 'receive_init'
    assert ports[0].operator == Operator.F_INIT
    assert ports[1].name == 'send_output'
    assert ports[1].operator == Operator.O_F

    manager_client.request_peers.assert_called_with(
            element._instance_name.return_value)

    element._connect.assert_called_with(
            *manager_client.request_peers.return_value)

    manager_client.get_configuration.assert_called_with()
    assert (manager_client.get_configuration.return_value ==
            element._configuration_store.base)


def test_register2(log_file_in_tmpdir) -> None:
    muscle = Muscle3()
    manager_client = MagicMock()
    manager_client.request_peers = MagicMock(return_value=(1, 2, 3))
    muscle._Muscle3__manager = manager_client

    element = MagicMock()
    element._name = Reference('test_model')
    element._index = [13, 42]
    element._declared_ports = {
            Operator.O_I: ['out_x', 'out_y'],
            Operator.B: ['in_x', 'in_y']}
    muscle.register([element])

    args = manager_client.register_instance.call_args[0]
    assert args[0] == Reference('test_model[13][42]')
    assert args[1] == element._communicator.get_locations.return_value
    ports = sorted(args[2], key=lambda port: port.name)
    assert ports[0].name == 'in_x'
    assert ports[0].operator == Operator.B
    assert ports[1].name == 'in_y'
    assert ports[1].operator == Operator.B
    assert ports[2].name == 'out_x'
    assert ports[2].operator == Operator.O_I
    assert ports[3].name == 'out_y'
    assert ports[3].operator == Operator.O_I

    manager_client.request_peers.assert_called_with(
            element._instance_name.return_value)

    element._connect.assert_called_with(
            *manager_client.request_peers.return_value)
