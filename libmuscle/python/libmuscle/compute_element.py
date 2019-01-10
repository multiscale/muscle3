from typing import List, Union

from ymmsl import Reference

from libmuscle.communicator import Communicator, Message


class ComputeElement:
    """Represents a Compute Element instance in a MUSCLE3 simulation.

    This class provides a low-level send/receive API for the instance
    to use.
    """
    def __init__(self, instance: Reference) -> None:
        """Create a ComputeElement.

        Args:
            instance: The name of the instance represented by this
                class.
        """
        # Accessed directly by Muscle3, but not part of public API.
        self._communicator = Communicator(instance)
        """Communicator for this instance."""

    def send_message(self, port_name: str, message: Union[bytes, Message],
                     slot: Union[int, List[int]]=[]) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        self._communicator.send_message(port_name, message, slot)

    def receive_message(self, port_name: str, decode: bool,
                        slot: Union[int, List[int]]=[]) -> Message:
        """Receive a message from the outside world.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            decode: Whether to MsgPack-decode the message (True) or
                    return raw bytes() (False).
            slot: The slot to receive the message on, if any.

        Returns:
            The received message, decoded from MsgPack if decode is
            True, otherwise as a raw bytes object.
        """
        return self._communicator.receive_message(port_name, decode, slot)
