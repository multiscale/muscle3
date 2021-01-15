from enum import IntEnum
from typing import Any, cast, Optional

import msgpack
import numpy as np

from ymmsl import Reference, Settings

from libmuscle.grid import Grid


class ExtTypeId(IntEnum):
    """MessagePack extension type ids.

    MessagePack lets you define your own types as an extension to the
    built-in ones. These are distinguished by a number from 0 to 127.
    This class is our registry of extension type ids.
    """
    CLOSE_PORT = 0
    SETTINGS = 1
    GRID_INT32 = 2
    GRID_INT64 = 3
    GRID_FLOAT32 = 4
    GRID_FLOAT64 = 5
    GRID_BOOL = 6


_grid_types = {
        ExtTypeId.GRID_INT32,
        ExtTypeId.GRID_INT64,
        ExtTypeId.GRID_FLOAT32,
        ExtTypeId.GRID_FLOAT64,
        ExtTypeId.GRID_BOOL}


class ClosePort:
    """Sentinel value to send when closing a port.

    Sending an object of this class on a port/conduit conveys to the
    receiver the message that no further messages will be sent on this
    port during the simulation.

    All information is carried by the type, this has no attributes.
    """
    pass


def _encode_grid(grid: Grid) -> msgpack.ExtType:
    """Encodes a Grid object into the wire format.
    """
    ext_type_map = {
            'int32': ExtTypeId.GRID_INT32,
            'int64': ExtTypeId.GRID_INT64,
            'float32': ExtTypeId.GRID_FLOAT32,
            'float64': ExtTypeId.GRID_FLOAT64,
            'bool': ExtTypeId.GRID_BOOL}

    array = grid.array
    if array.flags.f_contiguous:
        # indexes that differ in the first place are adjacent
        order = 'fa'
    else:
        # indexes that differ in the last place are adjacent
        order = 'la'

    # dtype is a bit weird, but this seems to be consistent
    if isinstance(array.dtype, np.dtype):
        array_type = str(array.dtype)
    else:
        array_type = str(np.dtype(array_type))

    if array_type not in ext_type_map:
        raise RuntimeError('Unsupported array data type')

    buf = array.tobytes(order='A')

    # array_type is redundant, but useful metadata.
    grid_dict = {
            'type': array_type,
            'shape': list(array.shape),
            'order': order,
            'data': buf,
            'indexes': grid.indexes}
    packed_data = msgpack.packb(grid_dict, use_bin_type=True)
    return msgpack.ExtType(ext_type_map[array_type], packed_data)


def _decode_grid(code: int, data: bytes) -> Grid:
    """Creates a Grid from serialised data.
    """
    type_map = {
            ExtTypeId.GRID_INT32: np.int32,
            ExtTypeId.GRID_INT64: np.int64,
            ExtTypeId.GRID_FLOAT32: np.float32,
            ExtTypeId.GRID_FLOAT64: np.float64,
            ExtTypeId.GRID_BOOL: np.bool8}

    order_map = {
            'fa': 'F',
            'la': 'C'}

    grid_dict = msgpack.unpackb(data, raw=False)
    order = order_map[grid_dict['order']]
    shape = tuple(grid_dict['shape'])
    dtype = type_map[ExtTypeId(code)]
    array = np.ndarray(shape, dtype, grid_dict['data'], order=order)
    indexes = grid_dict['indexes']
    if indexes == []:
        indexes = None
    return Grid(array, indexes)


def _data_encoder(obj: Any) -> Any:
    """Encodes custom objects for MessagePack.

    In particular, this takes care of any Settings, Grid and
    numpy.ndarray objects the user may want to send.
    """
    if isinstance(obj, ClosePort):
        return msgpack.ExtType(ExtTypeId.CLOSE_PORT, bytes())
    elif isinstance(obj, Settings):
        packed_data = msgpack.packb(obj.as_ordered_dict(),
                                    use_bin_type=True)
        return msgpack.ExtType(ExtTypeId.SETTINGS, packed_data)
    elif isinstance(obj, np.ndarray):
        return _encode_grid(Grid(obj))
    elif isinstance(obj, Grid):
        return _encode_grid(obj)
    return obj


def _ext_decoder(code: int, data: bytes) -> msgpack.ExtType:
    if code == ExtTypeId.CLOSE_PORT:
        return ClosePort()
    elif code == ExtTypeId.SETTINGS:
        plain_dict = msgpack.unpackb(data, raw=False)
        return Settings(plain_dict)
    elif code in _grid_types:
        return _decode_grid(code, data)
    return msgpack.ExtType(code, data)


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
        if isinstance(data, np.ndarray):
            self.data = Grid(data)
        else:
            self.data = data

    @staticmethod
    def from_bytes(message: bytes) -> 'Message':
        """Create an MCP Message from an encoded buffer.

        Args:
            message: MessagePack encoded message data.
        """
        message_dict = msgpack.unpackb(
                message, ext_hook=_ext_decoder, raw=False)
        sender = Reference(message_dict["sender"])
        receiver = Reference(message_dict["receiver"])
        port_length = message_dict["port_length"]
        timestamp = message_dict["timestamp"]
        next_timestamp = message_dict["next_timestamp"]
        settings_overlay = message_dict["settings_overlay"]

        data = message_dict["data"]
        return Message(sender, receiver, port_length, timestamp,
                       next_timestamp, settings_overlay, data)

    def encoded(self) -> bytes:
        """Encode the message and return as a bytes buffer.
        """
        message_dict = {
                'sender': str(self.sender),
                'receiver': str(self.receiver),
                'port_length': self.port_length,
                'timestamp': self.timestamp,
                'next_timestamp': self.next_timestamp,
                'settings_overlay': self.settings_overlay,
                'data': self.data
                }

        return cast(bytes, msgpack.packb(
            message_dict, default=_data_encoder, use_bin_type=True))
