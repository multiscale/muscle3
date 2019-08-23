import multiprocessing as mp
from typing import Dict

import msgpack
import pytest
from ymmsl import Reference

from libmuscle.outbox import Outbox
from libmuscle.post_office import PostOffice
from libmuscle.mcp.message import Message


def test_create(tcp_server):
    assert tcp_server['instance_id'] == Reference('test_sender')


def test_location(tcp_server):
    assert tcp_server['location'].startswith('tcp:')


def do_request(location, receiver):
    import pynng
    with pynng.Req0(dial=location) as sock:
        sock.send(receiver.encode('utf-8'))
        databuf = sock.recv()

    message_dict = msgpack.unpackb(databuf, raw=False)
    assert message_dict['sender'] == 'test_sender.test_port'
    assert message_dict['receiver'] == str(receiver)
    assert message_dict['port_length'] is None
    assert message_dict['timestamp'] == 0.0
    assert message_dict['next_timestamp'] == 1.0
    assert message_dict['parameter_overlay'] == bytes()
    assert message_dict['data'] == bytes()


def test_request(receiver, post_office, tcp_server):
    location = 'tcp://{}'.format(tcp_server['location'][4:])

    # Do NNG in a subprocess, not in the main process, to avoid forking
    # problems later.
    proc = mp.Process(
            target=do_request,
            args=(location, str(receiver)))
    proc.start()
    proc.join()
    assert proc.exitcode == 0
