from multiprocessing import Process
import os
from pathlib import Path
from typing import Sequence

from muscle3.muscle_manager import _manage_simulation


def manage_simulation(
        ymmsl_path: str, codes_path: str, ymmsl_files: Sequence[str]) -> None:
    """Set environment and run the simulation.

    Note that the environment needs to be set within the subprocess for this to work on
    platforms that don't use fork, which includes POSIX on Python 3.14 and up.
    """
    os.environ['YMMSL_PATH'] = ymmsl_path
    os.environ['PYTHONPATH'] = ':'.join([codes_path, os.environ.get('PYTHONPATH', '')])
    _manage_simulation(ymmsl_files, True, None, None, None, None)


def test_model_imports(ymmsl_path, codes_path, log_file_in_tmpdir) -> None:
    this_dir = Path(__file__).parent
    ymmsl_files = [str(this_dir / 'ymmsl' / 'models' / 'macro_micro_import.ymmsl')]
    proc = Process(
            target=manage_simulation, args=(ymmsl_path, codes_path, ymmsl_files),
            name='test_model_imports')
    proc.start()
    proc.join()
    assert proc.exitcode == 0
