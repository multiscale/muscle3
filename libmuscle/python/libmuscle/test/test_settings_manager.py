import pytest
from ymmsl import Reference, Settings

from libmuscle.settings_manager import SettingsManager


@pytest.fixture
def settings_manager() -> SettingsManager:
    return SettingsManager()


def test_create(settings_manager):
    assert len(settings_manager.base) == 0
    assert len(settings_manager.overlay) == 0


def test_list_settings_globals(settings_manager):
    ref = Reference
    settings_manager.base[ref('test1')] = 13
    settings_manager.base[ref('test2')] = 14
    assert settings_manager.list_settings(ref('macro')) == ['test1', 'test2']


def test_list_settings_specifics(settings_manager):
    ref = Reference
    settings_manager.base[ref('macro.test1')] = 'test1'
    settings_manager.base[ref('micro.test2')] = 'test2'
    assert settings_manager.list_settings(ref('macro')) == ['test1']

    settings_manager.base[ref('micro.test1')] = 'test1'
    assert settings_manager.list_settings(ref('macro')) == ['test1']


def test_list_settings_override(settings_manager):
    ref = Reference
    settings_manager.base[ref('test1')] = 'test1'
    settings_manager.base[ref('macro.test1')] = 42
    assert settings_manager.list_settings(ref('macro')) == ['test1']

    settings_manager.base[ref('micro.test1')] = 43
    assert settings_manager.list_settings(ref('macro')) == ['test1']

    settings_manager.base[ref('test2')] = 'test2'
    assert settings_manager.list_settings(ref('macro')) == ['test1', 'test2']


def test_list_settings_overlay(settings_manager):
    ref = Reference
    settings_manager.base[ref('test1')] = 'test1'
    settings_manager.overlay[ref('test1')] = 'test1'
    assert settings_manager.list_settings(ref('macro')) == ['test1']

    settings_manager.overlay[ref('test2')] = 'test2'
    assert settings_manager.list_settings(ref('macro')) == ['test1', 'test2']


def test_list_settings_overlay_override(settings_manager):
    ref = Reference
    settings_manager.base[ref('test1')] = 'test1'
    settings_manager.base[ref('micro.test2')] = 1
    settings_manager.overlay[ref('macro.test1')] = 13
    settings_manager.overlay[ref('micro.test2')] = 2

    assert settings_manager.list_settings(ref('macro')) == ['test1']
    assert settings_manager.list_settings(ref('micro')) == ['test1', 'test2']
    assert settings_manager.list_settings(ref('meso')) == ['test1']


def test_get_setting(settings_manager):
    ref = Reference
    settings_manager.base[ref('test')] = 13
    assert settings_manager.get_setting(ref('instance'), ref('test')) == 13

    settings_manager.overlay[ref('test2')] = 14
    assert settings_manager.get_setting(ref('instance'), ref('test2')) == 14

    settings_manager.base[ref('test2')] = 'test'
    assert settings_manager.get_setting(ref('instance'), ref('test2')) == 14

    settings_manager.overlay = Settings()
    assert settings_manager.get_setting(ref('instance'), ref('test2')) == \
        'test'

    settings_manager.base[ref('test3')] = 'base_test3'
    settings_manager.base[ref('instance.test3')] = 'base_instance_test3'
    assert settings_manager.get_setting(ref('instance'), ref('test3')) == \
        'base_instance_test3'
    assert settings_manager.get_setting(ref('instance2'), ref('test3')) == \
        'base_test3'

    settings_manager.overlay[ref('test3')] = 'overlay_test3'
    settings_manager.overlay[ref('instance.test3')] = 'overlay_instance_test3'
    assert settings_manager.get_setting(ref('instance'), ref('test3')) == \
        'overlay_instance_test3'
    assert settings_manager.get_setting(ref('instance2'), ref('test3')) == \
        'overlay_test3'

    settings_manager.base[ref('instance.test4')] = 'base_test4'
    settings_manager.overlay[ref('test4')] = 'overlay_test4'
    assert settings_manager.get_setting(ref('instance'), ref('test4')) == \
        'base_test4'

    assert settings_manager.get_setting(ref('instance[10]'), ref('test4')
                                        ) == 'base_test4'

    settings_manager.base[ref('instance[10].test5')] = 'base_test5'
    settings_manager.overlay[ref('test5')] = 'overlay_test5'
    assert settings_manager.get_setting(ref('instance'), ref('test5')) == \
        'overlay_test5'
    assert settings_manager.get_setting(ref('instance[10]'), ref('test5')
                                        ) == 'base_test5'
    assert settings_manager.get_setting(ref('instance[11]'), ref('test5')
                                        ) == 'overlay_test5'
