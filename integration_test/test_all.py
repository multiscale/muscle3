from unittest.mock import patch

import pytest
from ymmsl import Conduit, Operator, Reference

from libmuscle.mmp_client import MMPClient
from libmuscle.communicator import Communicator


def test_all(mmp_server):
    """A positive all-up test of everything.
    """
    # register macro
    macro = Reference('macro')
    macro_comm = Communicator(macro)
    macro_client = MMPClient('localhost:9000')
    macro_client.register_instance(macro, macro_comm.get_locations(), [])

    # register micros
    micro_clients = list()
    micro_comms = list()
    for i in range(100):
        micro_client = MMPClient('localhost:9000')
        micro_clients.append(micro_client)
        micro_instance = Reference('micro[{}][{}]'.format(i // 10, i % 10))
        communicator2 = Communicator(micro_instance)
        micro_comms.append(communicator2)
        micro_client.register_instance(
                micro_instance, communicator2.get_locations(), [])

    # wire up macro
    conduits, peer_dims, peer_locations = macro_client.request_peers(
            Reference('macro'))
    macro_comm.connect(conduits, peer_dims, peer_locations)

    # wire up micros
    for i in range(100):
        instance = Reference('micro[{}][{}]'.format(i // 10, i % 10))
        conduits, peer_dims, peer_locations = micro_clients[i].request_peers(
                instance)
        micro_comms[i].connect(conduits, peer_dims, peer_locations)

    # send and receive some messages
    macro_comm.send_message('out', 'testing', [0, 0])
    msg = micro_comms[0].receive_message('in', True)
    assert msg == 'testing'

    micro_comms[0].send_message('out', 'testing back')
    msg = macro_comm.receive_message('in', True, [0, 0])
    assert msg == 'testing back'

    macro_comm.send_message('out', [1, 2, 3], [3, 4])
    msg = micro_comms[34].receive_message('in', True)
    assert msg == [1, 2, 3]
