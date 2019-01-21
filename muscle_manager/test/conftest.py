import pytest
from ymmsl import Reference

from libmuscle.configuration import Configuration

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServicer
from muscle_manager.topology_store import TopologyStore


@pytest.fixture
def logger():
    return Logger()


@pytest.fixture
def configuration():
    return Configuration()


@pytest.fixture
def instance_registry():
    return InstanceRegistry()


@pytest.fixture
def topology_store() -> TopologyStore:
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10, 10]\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n')

    return TopologyStore(ymmsl_text)


@pytest.fixture
def mmp_servicer(logger, configuration, instance_registry, topology_store):
    return MMPServicer(logger, configuration, instance_registry,
                       topology_store)


@pytest.fixture
def loaded_instance_registry(instance_registry):
    instance_registry.add(Reference('macro'), ['direct:macro'], [])
    for j in range(10):
        for i in range(10):
            name = Reference('micro') + j + i
            location = 'direct:{}'.format(name)
            instance_registry.add(name, [location], [])
    return instance_registry


@pytest.fixture
def registered_mmp_servicer(logger, configuration, loaded_instance_registry,
                            topology_store):
    return MMPServicer(logger, configuration, loaded_instance_registry,
                       topology_store)


@pytest.fixture
def topology_store2() -> TopologyStore:
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    meso:\n'
            '      implementation: meso_implementation\n'
            '      multiplicity: 5\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [5, 10]\n'
            '  conduits:\n'
            '    macro.out: meso.in\n'
            '    meso.out: micro.in\n'
            '    micro.out: meso.in\n'
            '    meso.out: macro.in\n')

    return TopologyStore(ymmsl_text)


@pytest.fixture
def loaded_instance_registry2(instance_registry):
    instance_registry.add(Reference('macro'), ['direct:macro'], [])

    for j in range(5):
        name = Reference('meso') + j
        location = 'direct:{}'.format(name)
        instance_registry.add(name, [location], [])

    for j in range(5):
        for i in range(10):
            name = Reference('micro') + j + i
            location = 'direct:{}'.format(name)
            instance_registry.add(name, [location], [])
    return instance_registry


@pytest.fixture
def registered_mmp_servicer2(
        logger, configuration, loaded_instance_registry2, topology_store2):
    return MMPServicer(logger, configuration, loaded_instance_registry2,
                       topology_store2)
