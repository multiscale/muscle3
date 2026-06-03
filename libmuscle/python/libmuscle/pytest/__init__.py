import pytest
from typing import Iterator
from pathlib import Path

from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.pytest.muscle_tester import MuscleTester

__all__ = ["ImplementationTester", "MuscleTester"]


def _print_error_logs(run_dir: Path) -> None:
    """Print ERROR-level lines from the manager log file and show its path.

    Args:
        run_dir: The run directory containing muscle3_manager.log.
    """
    log_file = run_dir / "muscle3_manager.log"

    error_lines = [
        line for line in log_file.read_text().splitlines()
        if " ERROR " in line
    ]

    if error_lines:
        for line in error_lines:
            print(f"\n[muscle3_tester] {line}")
    print(f"\n[muscle3_tester] Full log: {log_file}")


@pytest.fixture
def muscle3_tester(tmp_path: Path) -> Iterator[MuscleTester]:
    """Pytest fixture providing a MuscleTester instance."""
    run_dir = tmp_path / "run_dir"
    with MuscleTester(run_dir) as tester:
        yield tester
    _print_error_logs(run_dir)
