import contextlib
import pytest

from libmuscle.pytest.muscle_tester import MuscleTester

__all__ = ["MuscleTester"]


@pytest.fixture
def muscle3_tester(tmp_path):
    with MuscleTester(tmp_path / "run_dir") as tester:
        yield tester
