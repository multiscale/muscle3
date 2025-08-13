import itertools
from pathlib import Path
import sys
import time
from typing import Generator, List, Optional, cast

from ymmsl import Reference


def instance_to_kernel(instance: Reference) -> Reference:
    """Extracts the name of the kernel from an instance name.

    Args:
        instance: The name of a kernel instance.

    Returns:
        The name of its kernel.
    """
    i = len(instance)
    while isinstance(instance[i - 1], int):
        i -= 1
    return instance[:i]


def instance_indices(instance: Reference) -> List[int]:
    """Extracts the indices from an instance name.

    Args:
        instance: The name of a kernel instance.

    Returns:
        The name of its kernel.
    """
    i = len(instance)
    while isinstance(instance[i - 1], int):
        i -= 1

    # Note that the slice operator on References returns a Reference,
    # which we don't want here.
    return [cast(int, instance[j]) for j in range(i, len(instance))]


def generate_indices(dims: List[int]) -> Generator[List[int], None, None]:
    """Generates all indices in a block of the given dimensions.

    Args:
        dims: The dimensions of the block.

    Yields:
        Lists of indices, one for each point in the block.
    """
    for index in itertools.product(*map(range, dims)):
        yield list(index)


def extract_log_file_location(filename: str) -> Optional[Path]:
    """Gets the log file location from the command line.

    Extracts the --muscle-log-file=<path> argument to tell the
    MUSCLE library where to write the local log file. This
    function will extract this argument from the command line
    arguments if it is present. If the given path is to a
    directory, <filename> will be written inside of that directory,
    if the path is not an existing directory, then it will be used
    as the name of the log file to write to. If no command line
    argument is given, this function returns None.

    Args:
        filename: Default file name to use.

    Returns:
        Path to the log file to write.
    """
    # Neither getopt, optparse, or argparse will let me pick out
    # just one option from the command line and ignore the rest.
    # So we do it by hand.
    prefix = '--muscle-log-file='
    given_path_str = None
    for arg in sys.argv[1:]:
        if arg.startswith(prefix):
            given_path_str = arg[len(prefix):]

    if not given_path_str:
        return None

    given_path = Path(given_path_str)

    if given_path.is_dir():
        return given_path / filename
    return given_path


_DEFAULT_BASE_DELAY = 0.5
_DEFAULT_TIMEOUT = 30.0
_FACTOR = 2.0 ** (1.0 / 3.0)


class Retrier:
    """Helper class for retrying things with a delay and timeout.

    This backs off exponentially, immediately retrying on the first attempt, then
    waiting 2**tries * base_delay seconds between tries.
    """
    def __init__(
            self, timeout: float = _DEFAULT_TIMEOUT,
            base_delay: float = _DEFAULT_BASE_DELAY
            ) -> None:
        """Create a Retrier.

        Args:
            timeout: Timeout in seconds after which to give up
            base_delay: Base delay in seconds between retries
        """
        self._base_delay = base_delay
        self._factor = _FACTOR
        self._timeout = timeout

        self._tries = 0
        self._start = 0.0

    def sleep(self) -> None:
        """Sleep until it's time for the next retry."""
        if self._tries == 0:
            delay = 0.0
        else:
            delay = self._base_delay * self._factor ** (self._tries - 1)

        time.sleep(delay)
        self._tries += 1

    def should_give_up(self) -> bool:
        """Return whether to give up or retry."""
        if self._tries == 0:
            self._start = time.monotonic()
        elapsed = time.monotonic() - self._start
        return elapsed >= self._timeout
