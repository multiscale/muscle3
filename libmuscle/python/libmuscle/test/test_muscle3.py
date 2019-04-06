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


def test_muscle_init_manager(log_file_in_tmpdir, sys_argv_manager) -> None:
    with patch('libmuscle.muscle3.MMPClient') as mock_client:
        Muscle3()
        mock_client.assert_called_once_with('localhost:9000')


def test_register(log_file_in_tmpdir) -> None:
    with patch('libmuscle.muscle3.MMPClient'):
        muscle = Muscle3()
        manager_client = MagicMock()
        manager_client.request_peers = MagicMock(return_value=(1, 2, 3))
        muscle._Muscle3__manager = manager_client
        muscle._Muscle3__profiler = MagicMock()

        element = MagicMock()
        element._name = Reference('test_model')
        element._index = []
        element._declared_ports = {
                Operator.F_INIT: ['receive_init'],
                Operator.O_F: ['send_output']}
        muscle.register([element])

        assert element._register.called_with()
        assert element._connect.called_with()
