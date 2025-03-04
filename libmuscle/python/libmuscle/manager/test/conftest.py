import pytest
from ymmsl import Component, Conduit, Configuration, Model, Reference

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPRequestHandler
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.snapshot_registry import SnapshotRegistry
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.manager.deadlock_detector import DeadlockDetector


@pytest.fixture
def logger(tmp_path):
    test_logger = Logger(tmp_path)
    yield test_logger
    test_logger.close()


@pytest.fixture
def mmp_configuration():
    return Configuration(
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


@pytest.fixture
def profile_store(tmp_path):
    test_profile_store = ProfileStore(tmp_path)
    yield test_profile_store
    test_profile_store.shutdown()


@pytest.fixture
def instance_registry():
    return InstanceRegistry()


@pytest.fixture
def topology_store(mmp_configuration) -> TopologyStore:
    return TopologyStore(mmp_configuration)


@pytest.fixture
def snapshot_registry(mmp_configuration, topology_store) -> SnapshotRegistry:
    return SnapshotRegistry(mmp_configuration, None, topology_store)


@pytest.fixture
def deadlock_detector() -> DeadlockDetector:
    return DeadlockDetector()


@pytest.fixture
def mmp_request_handler(
        logger, profile_store, mmp_configuration, instance_registry,
        topology_store, snapshot_registry, deadlock_detector):
    return MMPRequestHandler(
            logger, profile_store, mmp_configuration, instance_registry,
            topology_store, snapshot_registry, deadlock_detector, None)


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
        logger, profile_store, mmp_configuration, loaded_instance_registry,
        topology_store, snapshot_registry, deadlock_detector):
    return MMPRequestHandler(
            logger, profile_store, mmp_configuration, loaded_instance_registry,
            topology_store, snapshot_registry, deadlock_detector, None)


@pytest.fixture
def mmp_configuration2():
    return Configuration(
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


@pytest.fixture
def topology_store2(mmp_configuration2) -> TopologyStore:
    return TopologyStore(mmp_configuration2)


@pytest.fixture
def snapshot_registry2(mmp_configuration2, topology_store) -> SnapshotRegistry:
    return SnapshotRegistry(mmp_configuration2, None, topology_store)


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
        logger, profile_store, mmp_configuration, loaded_instance_registry2,
        topology_store2, snapshot_registry2, deadlock_detector, tmp_path):
    return MMPRequestHandler(
            logger, profile_store, mmp_configuration,
            loaded_instance_registry2, topology_store2, snapshot_registry2,
            deadlock_detector, RunDir(tmp_path))
