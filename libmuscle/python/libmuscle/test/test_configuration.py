import pytest
from ymmsl import Experiment, Reference, Setting

from libmuscle.configuration import Configuration


@pytest.fixture
def configuration():
    return Configuration()


def test_create_configuration(configuration):
    assert configuration._store == {}


def test_get_item(configuration):
    configuration._store[Reference('test')] = 13
    assert configuration[Reference('test')] == 13
    assert configuration['test'] == 13


def test_set_item(configuration):
    configuration['param1'] = 3
    assert configuration._store[Reference('param1')] == 3


def test_del_item(configuration):
    configuration._store = {Reference('param1'): 'test',
                            Reference('param2'): 0}
    del(configuration['param1'])
    assert len(configuration._store) == 1
    assert Reference('param1') not in configuration._store
    with pytest.raises(KeyError):
        configuration['param1']
    assert configuration._store['param2'] == 0


def test_iter(configuration):
    assert len(configuration) == 0
    for parameter, value in configuration:
        assert False    # pragma: no cover

    configuration._store = {
            Reference('test1'): 13,
            Reference('test2'): 'testing',
            Reference('test3'): [3.4, 5.6]}
    assert len(configuration) == 3

    for parameter in configuration:
        assert parameter in configuration

    for parameter, value in configuration.items():
        assert (
            parameter == 'test1' and value == 13 or
            parameter == 'test2' and value == 'testing' or
            parameter == 'test3' and value == [3.4, 5.6])


def test_update(configuration):
    config1 = Configuration()
    config1['param1'] = 13
    config1['param2'] = 'testing'

    configuration.update(config1)
    assert len(configuration) == 2
    assert configuration['param1'] == 13
    assert configuration['param2'] == 'testing'

    config2 = Configuration()
    config2['param2'] = [[1, 2], [2, 3]]
    config2['param3'] = 3.1415
    configuration.update(config2)
    assert len(configuration) == 3
    assert configuration['param1'] == 13
    assert configuration['param2'] == [[1, 2], [2, 3]]
    assert configuration['param3'] == 3.1415
