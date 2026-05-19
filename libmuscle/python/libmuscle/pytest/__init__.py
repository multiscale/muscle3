import pytest
from typing import Iterator
from pathlib import Path

from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.pytest.muscle_tester import MuscleTester

__all__ = ["ImplementationTester", "MuscleTester"]


@pytest.fixture
def muscle3_tester(tmp_path: Path) -> Iterator[MuscleTester]:
    """Pytest fixture providing a MuscleTester instance."""
    with MuscleTester(tmp_path / "run_dir") as tester:
        yield tester
