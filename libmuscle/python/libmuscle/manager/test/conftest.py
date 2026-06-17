import pytest
from ymmsl.v0_2 import Component, Conduit, Configuration, Model, Ports, Reference

from libmuscle.manager.deadlock_detector import DeadlockDetector
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPRequestHandler
from libmuscle.manager.profile_store import ProfileStore
from libmuscle.manager.run_dir import RunDir
from libmuscle.manager.snapshot_registry import SnapshotRegistry
from libmuscle.manager.topology_store import TopologyStore


@pytest.fixture
def logger(tmp_path):
    test_logger = Logger(tmp_path)
    yield test_logger
    test_logger.close()


@pytest.fixture
def mmp_configuration():
    return Configuration(
            'mmp_configuration', [], [Model(
                'test_model', None, '', None,
                [
                    Component(
                        'macro', Ports(o_i=['out'], s=['in']), '',
                        'macro_implementation'),
                    Component(
                        'micro', Ports(f_init=['in'], o_f=['out']), '',
                        'micro_implementation', False, [10, 10])],
                [
                    Conduit('macro.out', 'micro.in'),
                    Conduit('micro.out', 'macro.in')
                ])])


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
            location = f'direct:{name}'
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
            'mmp_configuration2', [], [Model(
                'test_model', None, '', None,
                [
                    Component(
                        'macro', Ports(o_i=['out'], s=['in']), '',
                        'macro_implementation'),
                    Component(
                        'meso',
                        Ports(f_init=['init'], o_i=['out'], s=['in'], o_f=['final']),
                        '', 'meso_implementation', False, [5]),
                    Component(
                        'micro', Ports(f_init=['init'], o_f=['final']), '',
                        'micro_implementation', False, [5, 10])
                ],
                [
                    Conduit('macro.out', 'meso.init'),
                    Conduit('meso.out', 'micro.init'),
                    Conduit('micro.final', 'meso.in'),
                    Conduit('meso.final', 'macro.in')
                ])])


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
        location = f'direct:{name}'
        instance_registry.add(name, [location], [])

    for j in range(5):
        for i in range(10):
            name = Reference('micro') + j + i
            location = f'direct:{name}'
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
