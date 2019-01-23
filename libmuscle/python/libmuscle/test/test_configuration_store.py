import pytest

from libmuscle.configuration import Configuration
from libmuscle.configuration_store import ConfigurationStore


@pytest.fixture
def store() -> ConfigurationStore:
    return ConfigurationStore()


def test_create(store):
    assert len(store._base) == 0
    assert len(store._overlay) == 0


def test_set_base(store):
    config = Configuration()
    store.set_base(config)
    assert store._base == config


def test_set_overlay(store):
    config = Configuration()
    store.set_overlay(config)
    assert store._overlay == config


def test_get_parameter(store):
    store._base['test'] = 13
    assert store.get_parameter('test') == 13

    store._overlay['test2'] = 14
    assert store.get_parameter('test2') == 14

    store._base['test2'] = 'test'
    assert store.get_parameter('test2') == 14

    store._overlay = Configuration()
    assert store.get_parameter('test2') == 'test'
