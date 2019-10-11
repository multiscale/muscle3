from enum import IntEnum
from typing import Any, cast, Optional

import msgpack

from ymmsl import Reference, Settings


class ExtTypeId(IntEnum):
    """MessagePack extension type ids.

    MessagePack lets you define your own types as an extension to the
    built-in ones. These are distinguished by a number from 0 to 127.
    This class is our registry of extension type ids.
    """
    CLOSE_PORT = 0
    SETTINGS = 1


class ClosePort:
    """Sentinel value to send when closing a port.

    Sending an object of this class on a port/conduit conveys to the
    receiver the message that no further messages will be sent on this
    port during the simulation.

    All information is carried by the type, this has no attributes.
    """
    pass


class Message:
    """A MUSCLE Communication Protocol message.

    Messages carry the identity of their sender and receiver, so that
    they can be routed by a MUSCLE Transport Overlay when we get to
    multi-site running in the future.
    """
    def __init__(self, sender: Reference, receiver: Reference,
                 port_length: Optional[int],
                 timestamp: float, next_timestamp: Optional[float],
                 settings_overlay: Settings, data: Any
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
            settings_overlay: The serialised overlay settings.
            data: The serialised contents of the message.
        """
        self.sender = sender
        self.receiver = receiver
        self.port_length = port_length
        self.timestamp = timestamp
        self.next_timestamp = next_timestamp
        self.settings_overlay = settings_overlay
        self.data = data

    @staticmethod
    def from_bytes(message: bytes) -> 'Message':
        """Create an MCP Message from an encoded buffer.

        Args:
            message: MessagePack encoded message data.
        """
        message_dict = msgpack.unpackb(message, raw=False)
        sender = Reference(message_dict["sender"])
        receiver = Reference(message_dict["receiver"])
        port_length = message_dict["port_length"]
        timestamp = message_dict["timestamp"]
        next_timestamp = message_dict["next_timestamp"]

        settings_dict = msgpack.unpackb(message_dict["settings_overlay"].data,
                                        raw=False)
        settings_overlay = Settings(settings_dict)

        data = message_dict["data"]
        if isinstance(data, msgpack.ExtType):
            if data.code == ExtTypeId.CLOSE_PORT:
                data = ClosePort()
            elif data.code == ExtTypeId.SETTINGS:
                plain_dict = msgpack.unpackb(data.data, raw=False)
                data = Settings(plain_dict)

        return Message(sender, receiver, port_length, timestamp,
                       next_timestamp, settings_overlay, data)

    def encoded(self) -> bytes:
        """Encode the message and return as a bytes buffer.
        """
        # pack overlay
        packed_overlay = msgpack.packb(self.settings_overlay.as_ordered_dict(),
                                       use_bin_type=True)
        overlay = msgpack.ExtType(ExtTypeId.SETTINGS, packed_overlay)

        # pack data
        if isinstance(self.data, ClosePort):
            data = msgpack.ExtType(ExtTypeId.CLOSE_PORT, bytes())
        elif isinstance(self.data, Settings):
            packed_data = msgpack.packb(self.data.as_ordered_dict(),
                                        use_bin_type=True)
            data = msgpack.ExtType(ExtTypeId.SETTINGS, packed_data)
        else:
            data = self.data

        # pack message
        message_dict = {
                'sender': str(self.sender),
                'receiver': str(self.receiver),
                'port_length': self.port_length,
                'timestamp': self.timestamp,
                'next_timestamp': self.next_timestamp,
                'settings_overlay': overlay,
                'data': data
                }

        return cast(bytes, msgpack.packb(message_dict, use_bin_type=True))
