from typing import Optional

from ymmsl import Reference


class Message:
    """A MUSCLE Communication Protocol message.

    Messages carry the identity of their sender and receiver, so that
    they can be routed by a MUSCLE Transport Overlay when we get to
    multi-site running in the future.
    """
    def __init__(self, sender: Reference, receiver: Reference,
                 port_length: Optional[int],
                 timestamp: float, next_timestamp: Optional[float],
                 parameter_overlay: bytes, data: bytes
                 ) -> None:
        """Create an MCPMessage.

        Senders and receivers are refered to by a Reference, which
        contains Instance[InstanceNumber].Port[Slot].

        The port_length field is only used if two vector ports are
        connected together. In that case the number of slots is not
        determined by the number of instances, and must be set by
        the sender and then communicated to the receiver in this
        additional field in all messages sent on the port.

        Args:
            sender: The sending endpoint.
            receiver: The receiving endpoint.
            port_length: Length of the slot, where applicable.
            parameter_overlay: The serialised overlay parameters.
            data: The serialised contents of the message.
        """
        self.sender = sender
        self.receiver = receiver
        self.port_length = port_length
        self.timestamp = timestamp
        self.next_timestamp = next_timestamp
        self.parameter_overlay = parameter_overlay
        self.data = data
