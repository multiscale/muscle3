from unittest.mock import patch

import pytest
from ymmsl import Conduit, Operator, Port, Reference

from libmuscle.mmp_client import MMPClient


def test_registration(log_file_in_tmpdir, mmp_server):
    client = MMPClient('localhost:9000')
    instance_name = Reference('test_instance')
    port = Port(Reference('test_in'), Operator.S)

    client.register_instance(instance_name, ['tcp://localhost:10000'],
                             [port])

    servicer = mmp_server._servicer
    registry = servicer._MMPServicer__instance_registry

    assert registry.get_locations(instance_name) == ['tcp://localhost:10000']
    assert registry.get_ports(instance_name)[0].name == 'test_in'
    assert registry.get_ports(instance_name)[0].operator == Operator.S


def test_wiring(log_file_in_tmpdir, mmp_server_process):
    client = MMPClient('localhost:9000')

    client.register_instance(Reference('macro'), ['direct:macro'], [])

    conduits, peer_dims, peer_locations = client.request_peers(
            Reference('micro[0]'))

    assert Conduit('macro.out', 'micro.in') in conduits
    assert Conduit('micro.out', 'macro.in') in conduits

    assert peer_dims[Reference('macro')] == []
    assert peer_locations['macro'] == ['direct:macro']

    with patch('libmuscle.mmp_client.PEER_TIMEOUT', 0.1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MIN', 0.01), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MAX', 0.1):
        with pytest.raises(RuntimeError):
            client.request_peers(Reference('macro'))

    for i in range(5):
        instance = Reference('micro[{}]'.format(i))
        location = 'direct:{}'.format(instance)
        client.register_instance(instance, [location], [])

    with patch('libmuscle.mmp_client.PEER_TIMEOUT', 0.1), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MIN', 0.01), \
            patch('libmuscle.mmp_client.PEER_INTERVAL_MAX', 0.1):
        with pytest.raises(RuntimeError):
            client.request_peers(Reference('macro'))

    for i in range(5, 10):
        instance = Reference('micro[{}]'.format(i))
        location = 'direct:{}'.format(instance)
        client.register_instance(instance, [location], [])

    conduits, peer_dims, peer_locations = client.request_peers(
            Reference('macro'))

    assert Conduit('macro.out', 'micro.in') in conduits
    assert Conduit('micro.out', 'macro.in') in conduits

    assert peer_dims[Reference('micro')] == [10]
    assert peer_locations['micro[7]'] == ['direct:micro[7]']
