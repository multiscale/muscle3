import pytest
from ymmsl import Reference, Settings

from libmuscle.configuration_store import ConfigurationStore


@pytest.fixture
def store() -> ConfigurationStore:
    return ConfigurationStore()


def test_create(store):
    assert len(store.base) == 0
    assert len(store.overlay) == 0


def test_get_parameter(store):
    ref = Reference
    store.base[ref('test')] = 13
    assert store.get_parameter(ref('instance'), ref('test')) == 13

    store.overlay[ref('test2')] = 14
    assert store.get_parameter(ref('instance'), ref('test2')) == 14

    store.base[ref('test2')] = 'test'
    assert store.get_parameter(ref('instance'), ref('test2')) == 14

    store.overlay = Settings()
    assert store.get_parameter(ref('instance'), ref('test2')) == 'test'

    store.base[ref('test3')] = 'base_test3'
    store.base[ref('instance.test3')] = 'base_instance_test3'
    assert store.get_parameter(ref('instance'), ref('test3')) == \
        'base_instance_test3'
    assert store.get_parameter(ref('instance2'), ref('test3')) == \
        'base_test3'

    store.overlay[ref('test3')] = 'overlay_test3'
    store.overlay[ref('instance.test3')] = 'overlay_instance_test3'
    assert store.get_parameter(ref('instance'), ref('test3')) == \
        'overlay_instance_test3'
    assert store.get_parameter(ref('instance2'), ref('test3')) == \
        'overlay_test3'

    store.base[ref('instance.test4')] = 'base_test4'
    store.overlay[ref('test4')] = 'overlay_test4'
    assert store.get_parameter(ref('instance'), ref('test4')) == \
        'base_test4'

    assert store.get_parameter(ref('instance[10]'), ref('test4')) == \
        'base_test4'

    store.base[ref('instance[10].test5')] = 'base_test5'
    store.overlay[ref('test5')] = 'overlay_test5'
    assert store.get_parameter(ref('instance'), ref('test5')) == \
        'overlay_test5'
    assert store.get_parameter(ref('instance[10]'), ref('test5')) == \
        'base_test5'
    assert store.get_parameter(ref('instance[11]'), ref('test5')) == \
        'overlay_test5'
