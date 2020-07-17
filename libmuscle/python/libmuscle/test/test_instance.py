import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Operator, Reference, Settings

from libmuscle.communicator import Message
from libmuscle.instance import Instance
from libmuscle.mcp.message import ClosePort
from libmuscle.settings_manager import SettingsManager


@pytest.fixture
def sys_argv_manager() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-manager=localhost:9000']
    yield None
    sys.argv = old_argv


@pytest.fixture
def log_file_in_tmpdir(tmpdir) -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = sys.argv + ['--muscle-log-file={}'.format(tmpdir)]
    yield None
    sys.argv = old_argv


@pytest.fixture
def sys_argv_instance() -> Generator[None, None, None]:
    old_argv = sys.argv
    sys.argv = ['', '--muscle-instance=test_instance[13][42]']
    yield
    sys.argv = old_argv


@pytest.fixture
def instance(sys_argv_instance):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator') as comm_type:
        communicator = MagicMock()
        settings = Settings()
        settings['test1'] = 12
        msg = Message(0.0, 1.0, 'message', settings)
        communicator.receive_message.return_value = msg
        comm_type.return_value = communicator

        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        mmp_client.return_value = mmp_client_object

        instance = Instance({
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.O_F: ['out']})
        instance._f_init_cache = dict()
        instance._f_init_cache[('in', None)] = msg
        yield instance


@pytest.fixture
def instance2(sys_argv_instance):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator'):
        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        mmp_client.return_value = mmp_client_object
        instance = Instance({
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out']})
        yield instance


def test_create_instance(
        sys_argv_instance, log_file_in_tmpdir, sys_argv_manager):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator') as comm_type:
        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        mmp_client.return_value = mmp_client_object
        ports = {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']}
        instance = Instance(ports)
        assert instance._name == Reference('test_instance')
        assert instance._index == [13, 42]
        assert instance._declared_ports == ports
        assert isinstance(instance._settings_manager, SettingsManager)
        assert len(instance._settings_manager.base) == 0
        assert len(instance._settings_manager.overlay) == 0
        mmp_client.assert_called_once_with('localhost:9000')
        assert mmp_client_object._register.called_with()
        assert mmp_client_object._connect.called_with()
        comm_type.assert_called_with(Reference('test_instance'), [13, 42],
                                     ports, instance._profiler)
        assert instance._communicator == comm_type.return_value
        assert isinstance(instance._settings_manager, SettingsManager)
        assert len(instance._settings_manager.base) == 0


def test_extract_manager_location(sys_argv_manager) -> None:
    assert (Instance._Instance__extract_manager_location() ==
            'localhost:9000')


def test_get_setting(instance):
    ref = Reference
    settings = Settings()
    settings[ref('test1')] = 'test'
    settings[ref('test2')] = 12
    settings[ref('test3')] = 27.1
    settings[ref('test4')] = True
    settings[ref('test5')] = [2.3, 5.6]
    settings[ref('test6')] = [[1.0, 2.0], [3.0, 4.0]]
    instance._settings_manager.base = settings

    assert instance.get_setting('test1') == 'test'
    assert instance.get_setting('test2') == 12
    assert instance.get_setting('test3') == 27.1
    assert instance.get_setting('test4') is True
    assert instance.get_setting('test5') == [2.3, 5.6]
    assert instance.get_setting('test6') == [
            [1.0, 2.0], [3.0, 4.0]]

    assert instance.get_setting('test1', 'str') == 'test'
    assert instance.get_setting('test2', 'int') == 12
    assert instance.get_setting('test3', 'float') == 27.1
    assert instance.get_setting('test4', 'bool') is True
    assert (instance.get_setting('test5', '[float]') ==
            [2.3, 5.6])
    assert (instance.get_setting('test6', '[[float]]') ==
            [[1.0, 2.0], [3.0, 4.0]])

    with pytest.raises(KeyError):
        instance.get_setting('testx')

    with pytest.raises(TypeError):
        instance.get_setting('test1', 'int')
    with pytest.raises(TypeError):
        instance.get_setting('test6', '[float]')
    with pytest.raises(TypeError):
        instance.get_setting('test5', '[[float]]')
    with pytest.raises(ValueError):
        instance.get_setting('test2', 'nonexistenttype')


def test_list_ports(instance):
    ports = instance.list_ports()
    assert instance._communicator.list_ports.called_with()
    assert ports == instance._communicator.list_ports.return_value


def test_is_vector_port(instance):
    instance._communicator.get_port.return_value.is_vector = MagicMock(
            return_value=True)
    is_vector = instance.is_vector_port('out_port')
    assert is_vector is True
    assert instance._communicator.get_port.called_with('out_port')


def test_send(instance, message):
    instance.send('out', message, 1)
    assert instance._communicator.send_message.called_with(
            'out', message, 1)


def test_send_invalid_port(instance, message):
    instance._communicator.port_exists.return_value = False
    with pytest.raises(RuntimeError):
        instance.send('does_not_exist', message, 1)


def test_receive(instance):
    instance._communicator.get_port.return_value = MagicMock(
            operator=Operator.F_INIT)
    msg = instance.receive('in')
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert instance._communicator.receive_message.called_with(
            'in', None)
    assert msg.data == 'message'

    with pytest.raises(RuntimeError):
        instance.receive('in')


def test_receive_default(instance):
    instance._communicator.port_exists.return_value = True
    port = instance._communicator.get_port.return_value
    port.operator = Operator.F_INIT
    port.is_connected.return_value = False
    instance.receive('not_connected', 1, 'testing')
    assert instance._communicator.receive_message.called_with(
            'not_connected', 1, 'testing')
    with pytest.raises(RuntimeError):
        instance.receive('not_connected', 1)


def test_receive_invalid_port(instance):
    instance._communicator.port_exists.return_value = False
    with pytest.raises(RuntimeError):
        instance.receive('does_not_exist', 1)


def test_receive_with_settings(instance):
    msg = instance.receive_with_settings('in', 1)
    assert (instance._communicator.receive_message
            .called_with('in', 1))
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.data == 'message'
    assert msg.settings['test1'] == 12


def test_receive_with_settings_default(instance):
    instance.receive_with_settings('not_connected', 1, 'testing')
    assert instance._communicator.receive_message.called_with(
            'not_connected', 1, 'testing')


def test_receive_parallel_universe(instance) -> None:
    instance._settings_manager.overlay['test2'] = 'test'
    with pytest.raises(RuntimeError):
        instance.receive('in')


def test_reuse_instance_receive_overlay(instance):
    instance._settings_manager.overlay = Settings()
    test_base_settings = Settings()
    test_base_settings['test1'] = 24
    test_base_settings['test2'] = [1.3, 2.0]
    test_overlay = Settings()
    test_overlay['test2'] = 'abc'
    recv = instance._communicator.receive_message
    recv.return_value = Message(0.0, None, test_overlay, test_base_settings)
    instance.reuse_instance()
    assert instance._communicator.receive_message.called_with(
        'muscle_settings_in')
    assert len(instance._settings_manager.overlay) == 2
    assert instance._settings_manager.overlay['test1'] == 24
    assert instance._settings_manager.overlay['test2'] == 'abc'


def test_reuse_instance_closed_port(instance):
    def receive_message(port_name, slot=None, default=None):
        if port_name == 'muscle_settings_in':
            return Message(0.0, None, Settings(), Settings())
        elif port_name == 'in':
            return Message(0.0, None, ClosePort(), Settings())
        assert False    # pragma: no cover

    def get_port(port_name):
        port = MagicMock()
        port.is_vector.return_value = False
        if port_name == 'not_connected':
            port.is_connected.return_value = False
        else:
            port.is_connected.return_value = True
        return port

    instance._communicator.receive_message = receive_message
    instance._communicator.list_ports.return_value = {
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.O_F: ['out']}
    instance._communicator.get_port = get_port
    instance._Instance__close_ports = MagicMock()

    do_reuse = instance.reuse_instance()
    assert do_reuse is False


def test_reuse_instance_vector_port(instance2):
    def receive_message(port_name, slot=None, default=None):
        if port_name == 'muscle_settings_in':
            return Message(0.0, None, Settings(), Settings())
        elif port_name == 'in':
            data = 'test {}'.format(slot)
            return Message(0.0, None, data, Settings())
        assert False    # pragma: no cover

    instance2._communicator.receive_message = receive_message
    instance2._communicator.list_ports.return_value = {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']}

    port = MagicMock()
    port.is_vector.return_value = True
    port.is_connected.return_value = True
    port.get_length.return_value = 10
    instance2._communicator.get_port.return_value = port

    do_reuse = instance2.reuse_instance()
    assert do_reuse is True

    msg = instance2.receive('in', 5)
    assert msg.timestamp == 0.0
    assert msg.next_timestamp is None
    assert msg.data == 'test 5'


def test_reuse_instance_no_f_init_ports(instance):
    instance._communicator.receive_message.return_value = Message(
            0.0, None, Settings(), Settings())
    instance._communicator.list_ports.return_value = {}
    instance._communicator.settings_in_connected.return_value = False
    do_reuse = instance.reuse_instance()
    assert do_reuse is True
    do_reuse = instance.reuse_instance()
    assert do_reuse is False


def test_reuse_instance_miswired(instance):
    with pytest.raises(RuntimeError):
        instance.reuse_instance()
