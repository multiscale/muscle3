import pytest
from typing import Iterator
from pathlib import Path

from libmuscle.pytest.implementation_tester import ImplementationTester
from libmuscle.pytest.muscle_tester import MuscleTester

__all__ = ["ImplementationTester", "MuscleTester"]


def _collect_log_report(run_dir: Path) -> str:
    """Collect ERROR- and CRITICAL-level lines from the manager log and instance log
    locations.

    Args:
        run_dir: The run directory containing muscle3_manager.log and instances.
    """
    log_file = run_dir / "muscle3_manager.log"

    lines = [f"Contents from: {log_file}", ""]

    error_lines = [
        line for line in log_file.read_text().splitlines()
        if " ERROR " in line or " CRITICAL " in line
    ]

    if error_lines:
        lines.extend(error_lines)

    lines += [
        "",
        "Instance log files can be found in:",
        f"  {run_dir / 'instances'}",
    ]

    return "\n".join(lines)


@pytest.fixture
def muscle3_tester(request: pytest.FixtureRequest, tmp_path: Path
                   ) -> Iterator[MuscleTester]:
    """Pytest fixture providing a MuscleTester instance."""
    run_dir = tmp_path / "run_dir"

    with MuscleTester(run_dir) as tester:
        yield tester

    report = _collect_log_report(run_dir)
    request.node.add_report_section("teardown", "muscle3 tester log", report)
