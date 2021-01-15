import struct

import msgpack
import numpy as np

from ymmsl import Reference, Settings

from libmuscle.grid import Grid
from libmuscle.mcp.message import Message


def test_create() -> None:
    sender = Reference('sender.port')
    receiver = Reference('receiver.port')
    timestamp = 10.0
    next_timestamp = 11.0
    settings_overlay = (6789).to_bytes(2, 'little', signed=True)
    data = (12345).to_bytes(2, 'little', signed=True)
    msg = Message(sender, receiver, None, timestamp, next_timestamp,
                  settings_overlay, data)
    assert msg.sender == sender
    assert msg.receiver == receiver
    assert msg.port_length is None
    assert msg.timestamp == 10.0
    assert msg.next_timestamp == 11.0
    assert msg.settings_overlay == settings_overlay
    assert msg.data == data


def test_grid_encode() -> None:
    sender = Reference('sender.port')
    receiver = Reference('receiver.port')
    timestamp = 10.0
    next_timestamp = 11.0

    array = np.array(
            [[[1.0, 2.0, 3.0],
              [4.0, 5.0, 6.0]],
             [[7.0, 8.0, 9.0],
              [10.0, 11.0, 12.0]]], np.float32)

    grid = Grid(array, ['x', 'y', 'z'])
    msg = Message(sender, receiver, None, timestamp, next_timestamp,
                  Settings(), grid)

    wire_data = msg.encoded()
    mcp_decoded = msgpack.unpackb(wire_data, raw=False)
    grid_decoded = msgpack.unpackb(mcp_decoded['data'].data, raw=False)

    assert grid_decoded['type'] == 'float32'
    assert grid_decoded['shape'] == [2, 2, 3]
    assert grid_decoded['order'] == 'la'
    next_value = 1.0
    for value in struct.iter_unpack('<f', grid_decoded['data']):
        assert value[0] == next_value
        next_value = next_value + 1.0

    assert grid_decoded['indexes'] == ['x', 'y', 'z']


def test_grid_decode() -> None:
    settings_data = msgpack.packb({}, use_bin_type=True)

    grid_buf = bytes(
            [1, 0, 0, 0,
             2, 0, 0, 0,
             3, 0, 0, 0,
             0, 0, 4, 0,
             0, 0, 5, 0,
             0, 0, 6, 0])

    grid_dict = {
            'type': 'int32',
            'shape': [2, 3],
            'order': 'la',
            'data': grid_buf,
            'indexes': []}
    grid_data = msgpack.packb(grid_dict, use_bin_type=True)

    msg_dict = {
            'sender': 'elem1.port1',
            'receiver': 'elem2.port2',
            'port_length': 0,
            'timestamp': 0.0,
            'next_timestamp': None,
            'settings_overlay': msgpack.ExtType(1, settings_data),
            'data': msgpack.ExtType(2, grid_data)}

    wire_data = msgpack.packb(msg_dict, use_bin_type=True)

    msg = Message.from_bytes(wire_data)

    assert isinstance(msg.data, Grid)
    assert msg.data.array.dtype == np.int32
    assert msg.data.array.shape == (2, 3)
    assert msg.data.array.flags.c_contiguous
    assert msg.data.array[0, 0] == 1
    assert msg.data.array[0, 1] == 2
    assert msg.data.array[1, 1] == 5 * 65536
    assert msg.data.indexes is None

    grid_dict['order'] = 'fa'
    grid_data = msgpack.packb(grid_dict, use_bin_type=True)
    msg_dict['data'] = msgpack.ExtType(2, grid_data)
    wire_data = msgpack.packb(msg_dict, use_bin_type=True)
    msg = Message.from_bytes(wire_data)

    assert isinstance(msg.data, Grid)
    assert msg.data.array.dtype == np.int32
    assert msg.data.array.shape == (2, 3)
    assert msg.data.array.flags.f_contiguous
    assert msg.data.array[0, 0] == 1
    assert msg.data.array[0, 1] == 3
    assert msg.data.array[0, 2] == 5 * 65536
    assert msg.data.indexes is None


def test_grid_roundtrip() -> None:
    sender = Reference('sender.port')
    receiver = Reference('receiver.port')
    timestamp = 10.0
    next_timestamp = 11.0

    for order in ('C', 'F'):
        array = np.array(
                [[[1.0, 2.0, 3.0],
                  [4.0, 5.0, 6.0]],
                 [[7.0, 8.0, 9.0],
                  [10.0, 11.0, 12.0]]], np.float64, order=order)

        assert array[0, 0, 0] == 1.0

        grid = Grid(array, ['x', 'y', 'z'])
        msg = Message(sender, receiver, None, timestamp, next_timestamp,
                      Settings(), grid)

        wire_data = msg.encoded()
        msg_out = Message.from_bytes(wire_data)

        assert isinstance(msg_out.data, Grid)
        grid_out = msg_out.data
        assert grid_out.indexes == ['x', 'y', 'z']
        assert isinstance(grid_out.array, np.ndarray)
        assert grid_out.array.dtype == np.float64
        assert grid_out.array.shape == (2, 2, 3)
        assert grid_out.array.size == 12
        assert grid_out.array[1, 0, 1] == 8.0
        assert grid_out.array[0, 0, 2] == 3.0


def test_non_contiguous_grid_roundtrip() -> None:
    sender = Reference('sender.port')
    receiver = Reference('receiver.port')
    timestamp = 10.0
    next_timestamp = 11.0

    array = np.array(
            [[[1.0 + 0.125j, 2.0 + 0.25j, 3.0 + 0.375j],
              [4.0 + 0.4375j, 5.0 + 0.5j, 6.0 + 0.625j]],
             [[7.0 + 0.75j, 8.0 + 0.875j, 9.0 + 0.9375j],
              [10.0 + 0.10j, 11.0 + 0.11j, 12.0 + 0.12j]]], np.complex64)

    assert array.real[0, 0, 0] == 1.0
    assert array.imag[0, 0, 0] == 0.125

    grid = Grid(array.real, ['a', 'b', 'c'])
    msg = Message(sender, receiver, None, timestamp, next_timestamp,
                  Settings(), grid)

    wire_data = msg.encoded()
    msg_out = Message.from_bytes(wire_data)

    assert isinstance(msg_out.data, Grid)
    grid_out = msg_out.data
    assert isinstance(grid_out.array, np.ndarray)
    assert grid_out.array.dtype == np.float32
    assert grid_out.array.shape == (2, 2, 3)
    assert grid_out.array.size == 12
    assert grid_out.array[1, 0, 1] == 8.0
    assert grid_out.array[0, 0, 2] == 3.0
