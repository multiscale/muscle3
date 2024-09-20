import logging
from pathlib import Path
from subprocess import Popen
from typing import Dict, List, Tuple


_logger = logging.getLogger(__name__)


class ProcessManager:
    """Manages a set of running processes."""
    def __init__(self) -> None:
        """Create a ProcessManager."""
        self._processes: Dict[str, Popen] = dict()

    def start(
            self, name: str, work_dir: Path, args: List[str], env: Dict[str, str],
            stdout: Path, stderr: Path) -> None:
        """Start a process.

        The files that the output is directed to will be overwritten if they already
        exist.

        Args:
            name: Name under which this process will be known
            work_dir: Working directory in which to start
            args: Executable and arguments to run
            env: Environment variables to set
            stdout: File to redirect stdout to
            stderr: File to redirect stderr to

        Raises:
            RuntimeError: If there is already a process with the given name.
            OSError: If the process could not be started.
        """
        if name in self._processes:
            raise RuntimeError(f'Process {name} already exists')
        _logger.debug(f'Starting process {args} with env {env} in {work_dir}')
        with stdout.open('w') as out, stderr.open('w') as err:
            self._processes[name] = Popen(
                    args, cwd=work_dir, env=env, stdout=out, stderr=err)

    def cancel_all(self) -> None:
        """Stops all running processes.

        This does not wait for them to terminate, it just sends the signal to kill
        them.
        """
        for process in self._processes.values():
            process.kill()

    def get_finished(self) -> List[Tuple[str, int]]:
        """Returns names and exit codes of finished processes.

        This returns all processes that have finished running since the previous call;
        each started process will be returned exactly once.
        """
        result: List[Tuple[str, int]] = list()

        for name, process in self._processes.items():
            exit_code = process.poll()
            if exit_code is not None:
                result.append((name, exit_code))

        for name, _ in result:
            del self._processes[name]

        return result
