import pytest
from ymmsl import Experiment, Reference, Setting

from libmuscle.configuration import Configuration


@pytest.fixture
def configuration():
    return Configuration()


def test_create_configuration(configuration):
    assert configuration._store == {}


def test_equality(configuration):
    conf2 = Configuration()
    assert configuration == conf2
    assert conf2 == configuration
    assert not (configuration != conf2)
    assert not (conf2 != configuration)

    conf1 = Configuration()
    conf1._store[Reference('x')] = 12
    conf1._store[Reference('y')] = 'test'
    conf1._store[Reference('z')] = [1.4, 5.3]

    conf2._store[Reference('x')] = 12
    conf2._store[Reference('y')] = 'test'
    conf2._store[Reference('z')] = [1.4, 5.3]

    assert conf1 == conf2
    assert conf2 == conf1

    conf3 = Configuration()
    conf3._store[Reference('x')] = 12
    conf3._store[Reference('z')] = [1.4, 5.3]

    assert conf3 != conf1
    assert conf1 != conf3

    conf4 = Configuration()
    conf4._store[Reference('x')] = 12
    conf4._store[Reference('y')] = 'test'
    conf4._store[Reference('z')] = [1.41, 5.3]

    assert conf1 != conf4
    assert conf4 != conf1
    assert conf3 != conf4
    assert conf4 != conf3

    assert conf1 != 'test'
    assert not (conf4 == 13)


def test_get_item(configuration):
    configuration._store[Reference('test')] = 13
    assert configuration[Reference('test')] == 13
    assert configuration['test'] == 13


def test_set_item(configuration):
    configuration['param1'] = 3
    assert configuration._store[Reference('param1')] == 3

    configuration[Reference('param2')] = 4
    assert configuration._store[Reference('param2')] == 4


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
    for parameter, value in configuration.items():
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


def test_copy():
    conf1 = Configuration()
    conf1['test'] = 12
    conf1['test2'] = [23, 12]
    conf1['test3'] = 'test3'

    conf2 = conf1.copy()

    assert conf1 == conf2
    conf2['test'] = 13
    assert conf2['test'] == 13
    assert conf1['test'] == 12

    conf2['test2'][0] = 24
    assert conf2['test2'] == [24, 12]
    assert conf1['test2'] == [24, 12]


def test_as_plain_dict(configuration):
    configuration._store = {
            Reference('test1'): 12,
            Reference('test2'): '12',
            Reference('test3'): 'testing',
            Reference('test4'): [12.3, 45.6]}
    conf_dict = configuration.as_plain_dict()
    assert conf_dict['test1'] == 12
    assert conf_dict['test2'] == '12'
    assert conf_dict['test3'] == 'testing'
    assert conf_dict['test4'] == [12.3, 45.6]
