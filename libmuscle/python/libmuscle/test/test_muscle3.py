from libmuscle import Muscle3

from unittest.mock import patch
import pytest
import sys
from typing import Generator


@pytest.fixture
def replaced_sys_argv() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv


def test_extract_manager_location(replaced_sys_argv) -> None:
    assert (Muscle3._Muscle3__extract_manager_location() ==
            'localhost:9000')


def test_muscle_init_no_manager() -> None:
    muscle = Muscle3()
    assert muscle._Muscle3__manager is None


def test_muscle_init_manager(replaced_sys_argv) -> None:
    with patch('libmuscle.muscle3.MMPClient') as mock_client:
        Muscle3()
        mock_client.assert_called_once_with('localhost:9000')
