from typing import Optional

from ymmsl import Reference


class Message:
    """A MUSCLE Communication Protocol message.

    Messages carry the identity of their sender and receiver, so that
    they can be routed by a MUSCLE Transport Overlay when we get to
    multi-site running in the future.
    """
    def __init__(self, sender: Reference, receiver: Reference,
                 timestamp: float, next_timestamp: Optional[float],
                 parameter_overlay: bytes, data: bytes
                 ) -> None:
        """Create an MCPMessage.

        Senders and receivers are refered to by a Reference, which
        contains ComputeElement[InstanceNumber].Port[Slot].

        Args:
            sender: The sending endpoint.
            receiver: The receiving endpoint.
            parameter_overlay: The serialised overlay parameters.
            data: The serialised contents of the message.
        """
        self.sender = sender
        self.receiver = receiver
        self.timestamp = timestamp
        self.next_timestamp = next_timestamp
        self.parameter_overlay = parameter_overlay
        self.data = data
