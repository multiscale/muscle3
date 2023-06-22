from typing import List, Optional, TypeVar

from ymmsl import Identifier, Operator
import ymmsl


_T = TypeVar("_T")


def _extend_list_to_size(lst: List[_T], size: int, padding: _T) -> None:
    """When lst is smaller than size, extend to size using padding as values
    """
    num_extend = size - len(lst)
    if num_extend > 0:
        lst += [padding] * num_extend


class Port(ymmsl.Port):
    """Represents a gateway to the outside world.

    Ports can be used to send or receive messages. They have a name and
    an operator, as well as a set of dimensions that determines the
    valid slot indices for sending or receiving on this port.

    Ports keep track of the amount of messages sent or received on the port.
    However, the actual incrementing and validation is done in
    :class:`Communicator`.

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
                self._length: Optional[int] = 0
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
        self._num_messages = [0] * (self._length or 1)
        self._is_resuming = [False] * (self._length or 1)

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
            # Using extend here to not discard any information about message
            # numbers between resizes. Note that _num_messages and _is_resuming
            # may be longer than self._length!
            _extend_list_to_size(self._num_messages, self._length, 0)
            _extend_list_to_size(self._is_resuming, self._length, False)

    def set_closed(self, slot: Optional[int] = None) -> None:
        """Marks this port as closed.
        """
        if slot is not None:
            self._is_open[slot] = False
        else:
            self._is_open = [False]

    def restore_message_counts(self, num_messages: List[int]) -> None:
        """Restore message counts from a snapshot
        """
        self._num_messages = num_messages
        self._is_resuming = [True] * len(self._num_messages)
        _extend_list_to_size(self._num_messages, self._length or 1, 0)
        _extend_list_to_size(self._is_resuming, self._length or 1, False)

    def get_message_counts(self) -> List[int]:
        """Get a list of message counts for all slots in this port
        """
        return self._num_messages.copy()

    def increment_num_messages(self, slot: Optional[int] = None) -> None:
        """Increment amount of messages sent or received.

        Args:
            slot: The slot that is sent/received on
        """
        self._num_messages[slot or 0] += 1
        self.set_resumed(slot)

    def get_num_messages(self, slot: Optional[int] = None) -> int:
        """Get the amount of messages sent or received.

        Args:
            slot: The slot that is sent/received on
        """
        return self._num_messages[slot or 0]

    def is_resuming(self, slot: Optional[int] = None) -> bool:
        """True when this port has resumed.

        After resumption, each port/slot may discard exactly one message.
        is_resuming keeps track of this state.

        Args:
            slot: The slot that is sent/received on
        """
        return self._is_resuming[slot or 0]

    def set_resumed(self, slot: Optional[int] = None) -> None:
        """Mark that this port has resumed and may no longer discard messages.

        Args:
            slot: The slot that is sent/received on
        """
        self._is_resuming[slot or 0] = False
