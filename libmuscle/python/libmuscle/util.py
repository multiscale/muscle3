from typing import List, cast

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
