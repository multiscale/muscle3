from typing import List

from ymmsl import Identifier, Reference


class Endpoint:
    """Place that a message is sent from and to.

    In the model description, we have kernels with ports connected by
    conduits. However, these kernels may be replicated, in which case
    there are many instances of them at run time. Thus, at run time
    there also need to be many conduit instances to connect the many
    kernel instances.

    A conduit always connects a port on a kernel to another port on
    another kernel. A conduit instance connects an endpoint to another
    endpoint. An endpoint has the name of a kernel, its index, the name
    of a port on that kernel, and a *slot*. The kernel and port name
    of a sender or receiver of a conduit instance come from the
    corresponding conduit.

    When a kernel is instantiated multiple times, the instances each
    have a unique index, which is a list of integers, to distinguish
    them from each other. Since a conduit instance connects kernel
    instances, each side will have an index to supply to the endpoint.
    The slot is an optional integer, like the index, and is passed when
    sending or receiving a message, and gives additional information
    on where to send the message.

    For example, assume a single kernel named ``abc`` with port ``p1``
    which is connected to a port ``p2`` on kernel ``def`` by a conduit,
    and of kernel ``def`` there are 10 instances. A message sent by
    ``abc`` on ``p1`` to the fourth instance of ``def`` port ``p2`` is
    sent from an endpoint with kernel ``abc``, index ``[]``, port
    ``p1`` and slot ``3``, and received on an endpoint with kernel
    ``def``, index ``[3]``, port ``p2`` and slot ``None``.

    Conduit instances are never actually created in the code, but
    Endpoints are.
    """
    def __init__(self, kernel: Reference, index: List[int], port: Identifier,
                 slot: List[int]) -> None:
        """Create an Endpoint

        Note: kernel is a Reference, not an Identifier, because it may
        have namespace parts.

        Args:
            kernel: Name of an instance's kernel.
            index: Index of the kernel instance.
            port: Name of the port used.
            slot: Slot on which to send or receive.
        """
        self.kernel = kernel  # type: Reference
        self.index = index    # type: List[int]
        self.port = port      # type: Identifier
        self.slot = slot      # type: List[int]

    def ref(self) -> Reference:
        """Express as Reference.

        This yields a valid Reference of the form
        kernel[index].port[slot], with index and port omitted if they
        are zero-length.

        Returns:
            A Reference to this Endpoint.
        """
        ret = self.kernel
        if self.index:
            ret += self.index
        ret += self.port
        if self.slot:
            ret += self.slot
        return ret

    def __str__(self) -> str:
        """Convert to string.

        Returns this Endpoint as the string for of a Reference to it.
        See :meth:ref().

        Returns:
            The string representation of this Endpoint.
        """
        return str(self.ref())

    def instance(self) -> Reference:
        """Get a Reference to the instance this endpoint is on.
        """
        ret = self.kernel
        if self.index:
            ret += self.index
        return ret
