from pathlib import Path
import sys
from typing import Generator, List, cast

from ymmsl import Conduit, Reference

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


def conduit_to_grpc(conduit: Conduit) -> mmp.Conduit:
    """Converts a ymmsl.Conduit to the corresponding mmp.Conduit.

    Args:
        conduit: A conduit.

    Returns:
        The same conduit, but grpc type.
    """
    return mmp.Conduit(sender=str(conduit.sender),
                       receiver=str(conduit.receiver))


def instance_to_kernel(instance: Reference) -> Reference:
    """Extracts the name of the kernel from an instance name.

    Args:
        instance: The name of a kernel instance.

    Returns:
        The name of its kernel.
    """
    i = len(instance)
    while isinstance(instance[i-1], int):
        i -= 1
    return cast(Reference, instance[:i])


def instance_indices(instance: Reference) -> List[int]:
    """Extracts the indices from an instance name.

    Args:
        instance: The name of a kernel instance.

    Returns:
        The name of its kernel.
    """
    i = len(instance)
    while isinstance(instance[i-1], int):
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
    index = [0] * len(dims)
    done = False
    while not done:
        yield index
        done = increment_index(index, dims)


def increment_index(index: List[int], dims: List[int]) -> bool:
    """Increments an index.

    Args:
        index: The index to be incremented.
        dims: The dimensions of the block this index is in.

    Returns:
        True iff the index overflowed and is now all zeros again.
    """
    cur = len(index) - 1
    index[cur] += 1
    while index[cur] == dims[cur]:
        index[cur] = 0
        if cur == 0:
            return True
        cur -= 1
        index[cur] += 1
    return False


def extract_log_file_location(run_dir: Path, filename: str) -> Path:
    """Gets the log file location from the command line.

    Extracts the --muscle-log-file=<path> argument to tell the
    MUSCLE library where to write the local log file. This
    function will extract this argument from the command line
    arguments if it is present. If the given path is to a
    directory, <filename> will be written inside of that directory,
    if the path is not an existing directory, then it will be used
    as the name of the log file to write to. If no command line
    argument is given, <filename> will be written in the specified
    directory.

    Args:
        run_dir: Default directory to use.
        filename: Default file name to use.

    Returns:
        Path to the log file to write.
    """
    # Neither getopt, optparse, or argparse will let me pick out
    # just one option from the command line and ignore the rest.
    # So we do it by hand.
    prefix = '--muscle-log-file='
    given_path_str = ''
    for arg in sys.argv[1:]:
        if arg.startswith(prefix):
            given_path_str = arg[len(prefix):]

    if given_path_str == '':
        return run_dir / filename

    given_path = Path(given_path_str)

    if given_path.is_dir():
        return given_path / filename
    return given_path
