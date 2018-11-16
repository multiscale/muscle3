from ymmsl import Operator, Reference

from libmuscle.endpoint import Endpoint
from libmuscle.mmp_client import MMPClient


def test_registration(mmp_server):
    client = MMPClient('localhost:9000')
    instance_name = Reference.from_string('test_instance')
    endpoint = Endpoint(
            Reference.from_string('test_in'),
            Operator.S)

    client.register_instance(instance_name, 'tcp://localhost:10000',
                             [endpoint])

    servicer = mmp_server._MMPServer__servicer
    registry = servicer._MMPServicer__instance_registry

    assert registry.get_location(instance_name) == 'tcp://localhost:10000'
    assert str(registry.get_endpoints(instance_name)[0].name) == 'test_in'
    assert registry.get_endpoints(instance_name)[0].operator == Operator.S
