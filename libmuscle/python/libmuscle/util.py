from typing import List, Generator, cast

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
    return instance[:i]


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
