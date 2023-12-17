from contextlib import nullcontext as does_not_raise
import sys
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest
from ymmsl import Operator, Reference, Settings, Checkpoints

from libmuscle.communicator import Message
from libmuscle.instance import Instance, InstanceFlags as IFlags
from libmuscle.mpp_message import ClosePort
from libmuscle.port import Port
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
def overlay_settings():
    settings = Settings()
    settings['test1'] = 12
    return settings


@pytest.fixture
def instance(sys_argv_instance, tmp_path, overlay_settings):
    ports = {
            Operator.F_INIT: ['in', 'not_connected'],
            Operator.S: ['in_s', 'in_settings', 'not_connected_s'],
            Operator.O_F: ['out', 'out_v']}

    def port_exists(name):
        return [name for op, names in ports.items() if name in names] != []

    def is_connected(name):
        return 'not_connected' not in name

    def is_vector(name):
        return name.endswith('_v')

    def get_port(name):
        return Port(
                name,
                [op for op, names in ports.items() if name in names][0],
                is_vector(name), is_connected(name), 2,
                [13, 42, 10] if is_vector(name) else [13, 42])

    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator') as comm_type:
        communicator = MagicMock()
        communicator.port_exists = MagicMock(side_effect=port_exists)
        communicator.is_connected = MagicMock(side_effect=is_connected)
        communicator.is_vector = MagicMock(side_effect=is_vector)
        communicator.get_port = MagicMock(side_effect=get_port)

        msg = Message(0.0, 1.0, 'message')
        msg_with_settings = Message(0.0, 1.0, 'message', overlay_settings)

        def receive_message(name, slot, default):
            if 'not_connected' in name:
                return default, 10.0
            if 'settings' in name:
                return msg_with_settings, 10.0
            return msg, 10.0

        communicator.receive_message = MagicMock(side_effect=receive_message)

        comm_type.return_value = communicator

        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)

        checkpoint_info = (0.0, Checkpoints(), None, tmp_path)
        mmp_client_object.get_checkpoint_info.return_value = checkpoint_info

        mmp_client.return_value = mmp_client_object

        instance = Instance(ports)
        instance._f_init_cache = dict()
        instance._f_init_cache[('in', None)] = msg

        yield instance


@pytest.fixture
def instance2(sys_argv_instance, tmp_path):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator'):
        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        checkpoint_info = (0.0, Checkpoints(), None, tmp_path)
        mmp_client_object.get_checkpoint_info.return_value = checkpoint_info
        mmp_client.return_value = mmp_client_object
        instance = Instance({
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out']})
        yield instance


def test_create_instance(
        sys_argv_instance, log_file_in_tmpdir, sys_argv_manager, tmp_path):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator') as comm_type:
        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        checkpoint_info = (0.0, Checkpoints(), None, tmp_path)
        mmp_client_object.get_checkpoint_info.return_value = checkpoint_info
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
        mmp_client.assert_called_once_with(
                Reference('test_instance[13][42]'), 'localhost:9000')
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
    instance._communicator.list_ports.assert_called_with()
    assert ports == instance._communicator.list_ports.return_value


def test_is_vector_port(instance):
    assert instance.is_vector_port('out_v')
    instance._communicator.get_port.assert_called_with('out_v')


def test_send(instance, message):
    instance._trigger_manager._cpts_considered_until = 17.0
    instance.send('out', message, 1)
    instance._communicator.send_message.assert_called_with('out', message, 1, 17.0)


def test_send_invalid_port(instance, message):
    with pytest.raises(RuntimeError):
        instance.send('does_not_exist', message, 1)


def test_receive(instance):
    msg = instance.receive('in_s')
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.data == 'message'
    instance._communicator.receive_message.assert_called_with('in_s', None, None)


def test_receive_cached(instance):
    msg = instance.receive('in')
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.data == 'message'
    instance._communicator.receive_message.assert_not_called()

    with pytest.raises(RuntimeError):
        instance.receive('in')


def test_receive_default(instance):
    default_msg = Message(1.0, 2.0, 'testing')
    msg = instance.receive('not_connected_s', 1, default_msg)
    instance._communicator.receive_message.assert_called_with(
            'not_connected_s', 1, default_msg)
    assert msg == default_msg


def test_receive_default_cached(instance):
    msg = instance.receive('not_connected', 1, Message(1.0, 2.0, 'testing'))
    assert msg.timestamp == 1.0
    assert msg.next_timestamp == 2.0
    assert msg.data == 'testing'
    instance._communicator.receive_message.assert_not_called()
    with pytest.raises(RuntimeError):
        instance.receive('not_connected', 1)


def test_receive_invalid_port(instance):
    with pytest.raises(RuntimeError):
        instance.receive('does_not_exist', 1)


def test_receive_with_settings(instance, overlay_settings):
    instance._settings_manager.overlay = overlay_settings
    msg = instance.receive_with_settings('in_settings')
    instance._communicator.receive_message.assert_called_with(
            'in_settings', None, None)
    assert msg.timestamp == 0.0
    assert msg.next_timestamp == 1.0
    assert msg.data == 'message'
    assert msg.settings['test1'] == 12


def test_receive_with_settings_default(instance):
    settings = Settings()
    settings['test1'] = 42
    default_msg = Message(1.0, 2.0, 'testing', settings)
    msg = instance.receive_with_settings('not_connected_s', default=default_msg)
    instance._communicator.receive_message.assert_called_with(
            'not_connected_s', None, msg)
    assert msg.settings['test1'] == 42


def test_receive_parallel_universe(instance) -> None:
    instance._settings_manager.overlay['test2'] = 'test'
    with pytest.raises(RuntimeError):
        instance.receive('in_settings')


def test_reuse_instance_receive_overlay(instance):
    instance._settings_manager.overlay = Settings()

    test_base_settings = Settings()
    test_base_settings['test1'] = 24
    test_base_settings['test2'] = [1.3, 2.0]

    test_overlay = Settings()
    test_overlay['test2'] = 'abc'

    msg = Message(0.0, None, test_overlay, test_base_settings)

    recv = instance._communicator.receive_message
    recv.reset_mock(side_effect=True)
    recv.return_value = msg, 0.0

    instance.reuse_instance()
    instance._communicator.receive_message.assert_called()
    assert instance._communicator.receive_message.call_args[0][0] == (
            'muscle_settings_in')

    assert len(instance._settings_manager.overlay) == 2
    assert instance._settings_manager.overlay['test1'] == 24
    assert instance._settings_manager.overlay['test2'] == 'abc'


def test_reuse_instance_closed_port(instance):
    def receive_message(port_name, slot=None, default=None):
        if port_name == 'muscle_settings_in':
            return Message(0.0, None, Settings(), Settings()), 0.0
        elif port_name == 'in':
            return Message(0.0, None, ClosePort(), Settings()), 1.0
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
            return Message(0.0, None, Settings(), Settings()), 0.0
        elif port_name == 'in':
            data = 'test {}'.format(slot)
            return Message(0.0, None, data, Settings()), 0.0
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
            0.0, None, Settings(), Settings()), 0.0
    instance._communicator.list_ports.return_value = {}
    instance._communicator.settings_in_connected.return_value = False
    do_reuse = instance.reuse_instance()
    assert do_reuse is True
    do_reuse = instance.reuse_instance()
    assert do_reuse is False


def test_reuse_instance_miswired(instance):
    with pytest.raises(RuntimeError):
        instance.reuse_instance()


@pytest.mark.parametrize('flags, expectation', [
        (IFlags(0), pytest.raises(RuntimeError)),
        (IFlags.USES_CHECKPOINT_API, does_not_raise()),
        (IFlags.KEEPS_NO_STATE_FOR_NEXT_USE, does_not_raise()),
        (IFlags.STATE_NOT_REQUIRED_FOR_NEXT_USE, does_not_raise())])
def test_checkpoint_support(sys_argv_instance, tmp_path, flags, expectation):
    with patch('libmuscle.instance.MMPClient') as mmp_client, \
         patch('libmuscle.instance.Communicator') as comm_type:
        comm_type.return_value = MagicMock()

        mmp_client_object = MagicMock()
        mmp_client_object.request_peers.return_value = (None, None, None)
        checkpoint_info = (0.0, Checkpoints(at_end=True), None, tmp_path)
        mmp_client_object.get_checkpoint_info.return_value = checkpoint_info
        mmp_client.return_value = mmp_client_object

        with expectation:
            Instance(flags=flags)
