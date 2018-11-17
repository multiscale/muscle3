import pytest

from ymmsl import Operator

from muscle_manager.instance_registry import Endpoint, InstanceRegistry


@pytest.fixture
def endpoint():
    return Endpoint('test_endpoint', Operator.F_INIT)


@pytest.fixture
def registry():
    return InstanceRegistry()


def test_endpoint(endpoint):
    assert endpoint.name == 'test_endpoint'
    assert endpoint.operator == Operator.F_INIT


def test_registry_add(registry, endpoint):
    registry.add('instance1', 'tcp://localhost:6253', [endpoint])
    assert (registry._InstanceRegistry__locations['instance1'] ==
            'tcp://localhost:6253')
    assert registry._InstanceRegistry__endpoints['instance1'] == [endpoint]


def test_registry_get(registry, endpoint):
    registry._InstanceRegistry__locations['instance1'] = 'tcp://localhost:6253'
    registry._InstanceRegistry__endpoints['instance1'] = [endpoint]
    assert registry.get_location('instance1') == 'tcp://localhost:6253'
    assert registry.get_endpoints('instance1') == [endpoint]

    with pytest.raises(KeyError):
        registry.get_location('non-existant-instance')

    with pytest.raises(KeyError):
        registry.get_endpoints('non-existant-instance')


def test_registry_remove(registry, endpoint):
    registry._InstanceRegistry__locations['instance1'] = 'tcp://localhost:6253'
    registry._InstanceRegistry__endpoints['instance1'] = [endpoint]
    registry.remove('instance1')
    assert 'instance1' not in registry._InstanceRegistry__locations
    assert 'instance1' not in registry._InstanceRegistry__endpoints

    with pytest.raises(KeyError):
        registry.remove('non-existant-instance')
