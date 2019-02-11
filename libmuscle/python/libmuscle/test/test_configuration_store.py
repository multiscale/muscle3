import pytest

from libmuscle.configuration import Configuration
from libmuscle.configuration_store import ConfigurationStore


@pytest.fixture
def store() -> ConfigurationStore:
    return ConfigurationStore()


def test_create(store):
    assert len(store.base) == 0
    assert len(store.overlay) == 0


def test_get_parameter(store):
    store.base['test'] = 13
    assert store.get_parameter('test') == 13

    store.overlay['test2'] = 14
    assert store.get_parameter('test2') == 14

    store.base['test2'] = 'test'
    assert store.get_parameter('test2') == 14

    store.overlay = Configuration()
    assert store.get_parameter('test2') == 'test'
