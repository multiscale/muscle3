import pytest

from ymmsl import Operator

from libmuscle.manager.instance_registry import Port, InstanceRegistry


@pytest.fixture
def port():
    return Port('test_port', Operator.F_INIT)


@pytest.fixture
def registry():
    return InstanceRegistry(['instance1'])


def test_port(port):
    assert port.name == 'test_port'
    assert port.operator == Operator.F_INIT


def test_registry_add(registry, port):
    registry.add('instance1', 'tcp://localhost:6253', [port])
    assert (registry._InstanceRegistry__locations['instance1'] ==
            'tcp://localhost:6253')
    assert registry._InstanceRegistry__ports['instance1'] == [port]


def test_registry_get(registry, port):
    registry._InstanceRegistry__locations['instance1'] = [
            'tcp://localhost:6253']
    registry._InstanceRegistry__ports['instance1'] = [port]
    assert registry.get_locations('instance1') == ['tcp://localhost:6253']
    assert registry.get_ports('instance1') == [port]

    with pytest.raises(KeyError):
        registry.get_locations('non-existant-instance')

    with pytest.raises(KeyError):
        registry.get_ports('non-existant-instance')


def test_registry_remove(registry, port):
    registry._InstanceRegistry__locations['instance1'] = [
            'tcp://localhost:6253']
    registry._InstanceRegistry__ports['instance1'] = [port]
    registry.remove('instance1')
    assert 'instance1' not in registry._InstanceRegistry__locations
    assert 'instance1' not in registry._InstanceRegistry__ports

    with pytest.raises(KeyError):
        registry.remove('non-existant-instance')
