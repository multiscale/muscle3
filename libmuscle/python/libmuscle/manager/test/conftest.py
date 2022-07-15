from pathlib import Path

import pytest
from ymmsl import (Component, Conduit, Configuration, Model, Reference,
                   Settings)

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPRequestHandler
from libmuscle.manager.topology_store import TopologyStore


@pytest.fixture
def logger(tmpdir):
    test_logger = Logger(Path(str(tmpdir)))
    yield test_logger
    test_logger.close()


@pytest.fixture
def settings():
    return Settings()


@pytest.fixture
def instance_registry():
    return InstanceRegistry()


@pytest.fixture
def topology_store() -> TopologyStore:
    config = Configuration(
            Model(
                'test_model',
                [
                    Component('macro', 'macro_implementation'),
                    Component(
                        'micro', 'micro_implementation', [10, 10])],
                [
                    Conduit('macro.out', 'micro.in'),
                    Conduit('micro.out', 'macro.in')
                ]))

    return TopologyStore(config)


@pytest.fixture
def mmp_request_handler(logger, settings, instance_registry, topology_store):
    return MMPRequestHandler(
            logger, settings, instance_registry, topology_store)


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
def registered_mmp_request_handler(
        logger, settings, loaded_instance_registry, topology_store):
    return MMPRequestHandler(
            logger, settings, loaded_instance_registry, topology_store)


@pytest.fixture
def topology_store2() -> TopologyStore:
    config = Configuration(
            Model(
                'test_model',
                [
                    Component('macro', 'macro_implementation'),
                    Component('meso', 'meso_implementation', [5]),
                    Component('micro', 'micro_implementation', [5, 10])
                ],
                [
                    Conduit('macro.out', 'meso.in'),
                    Conduit('meso.out', 'micro.in'),
                    Conduit('micro.out', 'meso.in'),
                    Conduit('meso.out', 'macro.in')
                ]))

    return TopologyStore(config)


@pytest.fixture
def loaded_instance_registry2():
    instance_registry = InstanceRegistry()

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
def registered_mmp_request_handler2(
        logger, settings, loaded_instance_registry2, topology_store2):
    return MMPRequestHandler(
            logger, settings, loaded_instance_registry2, topology_store2)
