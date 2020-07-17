from typing import List, Optional
from ymmsl import Identifier, Operator
import ymmsl

from libmuscle.operator import operator_from_grpc, operator_to_grpc
import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


# Convert between grpc and ymmsl Port types
def port_from_grpc(port: mmp.Port) -> ymmsl.Port:
    return ymmsl.Port(
            Identifier(port.name),
            operator_from_grpc(port.operator))


def port_to_grpc(port: ymmsl.Port) -> mmp.Port:
    return mmp.Port(
            name=str(port.name),
            operator=operator_to_grpc(port.operator))


def optional_port_to_grpc(port: Optional[ymmsl.Port]) -> Optional[mmp.Port]:
    if port is None:
        return None
    return port_to_grpc(port)


class Port(ymmsl.Port):
    """Represents a gateway to the outside world.

    Ports can be used to send or receive messages. They have a name and
    an operator, as well as a set of dimensions that determines the
    valid slot indices for sending or receiving on this port.

    Attributes:
        name (Identifier): Name of this port.
        operator (Operator): Operator associated with this port.
    """
    def __init__(self, name: str, operator: Operator, is_vector: bool,
                 is_connected: bool, our_ndims: int, peer_dims: List[int]
                 ) -> None:
        """Create a Port.

        Args:
            name: Name of this port.
            operator: Corresponding operator.
            is_vector: Whether this is a vector port.
            is_connected: Whether this port is connected to a peer.
            our_ndims: Number of dimensions of our instance set.
            peer_dims: Dimensions of the peer instance set of this port.
        """
        super().__init__(Identifier(name), operator)

        self._is_connected = is_connected

        if is_vector:
            if our_ndims == len(peer_dims):
                self._length = 0    # type: Optional[int]
            elif our_ndims + 1 == len(peer_dims):
                self._length = peer_dims[-1]
            elif our_ndims > len(peer_dims):
                raise RuntimeError(('Vector port "{}" is connected to an'
                                    ' instance set with fewer dimensions.'
                                    ' It should be connected to a scalar'
                                    ' port on a set with one more dimension,'
                                    ' or to a vector port on a set with the'
                                    ' same number of dimensions.').format(
                                        name))
            else:
                raise RuntimeError(('Port "{}" is connected to an instance set'
                                    ' with more than one dimension more than'
                                    ' its own, which is not possible.').format(
                                        name))
            self._is_open = [True] * self._length
        else:
            if our_ndims < len(peer_dims):
                raise RuntimeError(('Scalar port "{}" is connected to an'
                                    ' instance set with more dimensions.'
                                    ' It should be connected to a scalar'
                                    ' port on an instance set with the same'
                                    ' dimensions, or to a vector port on an'
                                    ' instance set with one less dimension.'
                                    ).format(name))
            elif our_ndims > len(peer_dims) + 1:
                raise RuntimeError(('Scalar port "{}" is connected to an'
                                    ' instance set with at least two fewer'
                                    ' dimensions, which is not possible.'
                                    ).format(name))
            self._length = None
            self._is_open = [True]

        self._is_resizable = is_vector and (our_ndims == len(peer_dims))

    # Note: I'm not sure how this will develop exactly, so this class has some
    # accessors even if those are un-Pythonic; in the future a simple variable
    # read may not be the right model.

    def is_connected(self) -> bool:
        """Returns whether the port is connected to a peer.

        Returns:
            True if there is a peer, False if there is not.
        """
        return self._is_connected

    def is_open(self, slot: Optional[int] = None) -> bool:
        """Returns whether this port is open.
        """
        if slot is not None:
            return self._is_open[slot]
        return self._is_open[0]

    def is_vector(self) -> bool:
        """Returns whether this is a vector port.

        Returns:
            True if it is vector, False if it is scalar.
        """
        return self._length is not None

    def is_resizable(self) -> bool:
        """Returns whether this port can be resized.
        """
        return self._is_resizable

    def get_length(self) -> int:
        """Returns the length of this port.

        Raises:
            RuntimeError: If this port is a scalar port.
        """
        if self._length is None:
            raise RuntimeError(('Tried to get length of scalar port {}'
                                ).format(self.name))
        return self._length

    def set_length(self, length: int) -> None:
        """Sets the length of a resizable vector port.

        Only call this if is_resizable() returns True.

        Args:
            length: The new length.

        Raises:
            RuntimeError: If the port is not resizable.
        """
        if not self._is_resizable:
            raise RuntimeError(('Tried to resize port {}, but it is not'
                                ' resizable.'.format(self.name)))
        if length != self._length:
            self._length = length
            self._is_open = [True] * self._length

    def set_closed(self, slot: Optional[int] = None) -> None:
        """Marks this port as closed.
        """
        if slot is not None:
            self._is_open[slot] = False
        else:
            self._is_open = [False]
