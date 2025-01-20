from contextlib import nullcontext as does_not_raise
import logging
from unittest.mock import MagicMock, patch

import pytest

from libmuscle.instance import Instance, InstanceFlags
from libmuscle.mpp_message import ClosePort
from ymmsl import Checkpoints, Operator, Reference as Ref, Settings


@pytest.fixture
def logger():
    with patch('libmuscle.instance._logger') as logger:
        yield logger


@pytest.fixture(autouse=True)
def MMPClient():
    with patch('libmuscle.instance.MMPClient') as MMPClient:
        mmp_client = MMPClient.return_value
        mmp_client.request_peers.return_value = (MagicMock(), MagicMock(), MagicMock())

        checkpoints = MagicMock()
        checkpoints.__bool__.return_value = False
        mmp_client.get_checkpoint_info.return_value = [
                MagicMock(), checkpoints, MagicMock(), MagicMock()]
        yield MMPClient


@pytest.fixture
def mmp_client(MMPClient):
    return MMPClient.return_value


@pytest.fixture
def api_guard():
    with patch('libmuscle.instance.APIGuard') as APIGuard:
        yield APIGuard.return_value


@pytest.fixture
def profiler():
    with patch('libmuscle.instance.Profiler') as Profiler:
        yield Profiler.return_value


@pytest.fixture
def port_manager():
    with patch('libmuscle.instance.PortManager') as PortManager:
        port_manager = PortManager.return_value
        port_manager.settings_in_connected.return_value = False
        yield port_manager


@pytest.fixture
def communicator():
    with patch('libmuscle.instance.Communicator') as Communicator:
        yield Communicator.return_value


@pytest.fixture
def settings_manager():
    with patch('libmuscle.instance.SettingsManager') as SettingsManager:
        settings_manager = SettingsManager.return_value
        # Emulate no settings available
        settings_manager.get_setting.side_effect = KeyError()
        yield settings_manager


@pytest.fixture(autouse=True)
def snapshot_manager():
    with patch('libmuscle.instance.SnapshotManager') as SnapshotManager:
        yield SnapshotManager.return_value


@pytest.fixture(autouse=True)
def no_resume_snapshot_manager(snapshot_manager):
    snapshot_manager.resuming_from_intermediate.return_value = False
    snapshot_manager.resuming_from_final.return_value = False
    snapshot_manager.resume_overlay = None
    return snapshot_manager


@pytest.fixture(autouse=True)
def trigger_manager():
    with patch('libmuscle.instance.TriggerManager') as TriggerManager:
        yield TriggerManager.return_value


@pytest.fixture
def sys_argv():
    with patch('libmuscle.instance.sys.argv', []) as sys_argv:
        yield sys_argv


@pytest.fixture
def manager_location_argv(sys_argv):
    sys_argv.extend(['--test', '--muscle-manager=tcp:localhost:9001', 'bla'])
    yield None


@pytest.fixture
def instance_argv(sys_argv):
    sys_argv.extend(['distraction', '--muscle-instance=component'])
    yield None


@pytest.fixture
def os_environ():
    with patch('libmuscle.instance.os.environ', {}) as os_environ:
        yield os_environ


@pytest.fixture
def manager_location_envvar(os_environ):
    os_environ['MUSCLE_MANAGER'] = 'tcp:localhost:9002'
    yield None


@pytest.fixture
def instance_envvar(os_environ):
    os_environ['MUSCLE_INSTANCE'] = 'component[13]'
    yield None


@pytest.fixture
def instance(
        logger, MMPClient, mmp_client, api_guard, profiler, connected_port_manager,
        communicator, settings_manager, no_resume_snapshot_manager, trigger_manager,
        manager_location_argv, instance_argv, declared_ports):

    return Instance(declared_ports)


@pytest.fixture
def instance_dont_apply_overlay(
        logger, MMPClient, mmp_client, api_guard, profiler, connected_port_manager,
        communicator, settings_manager, no_resume_snapshot_manager, trigger_manager,
        manager_location_argv, instance_argv, declared_ports):

    return Instance(declared_ports, InstanceFlags.DONT_APPLY_OVERLAY)


def test_create_instance_manager_location_default(
        instance_argv, MMPClient, declared_ports):

    instance = Instance(declared_ports)
    instance.error_shutdown("")  # ensure all threads and resources are cleaned up

    MMPClient.assert_called_once_with(Ref('component'), 'tcp:localhost:9000')


def test_create_instance_manager_location_argv(
        manager_location_argv, instance_argv, MMPClient, declared_ports):

    instance = Instance(declared_ports)
    instance.error_shutdown("")  # ensure all threads and resources are cleaned up

    MMPClient.assert_called_once_with(Ref('component'), 'tcp:localhost:9001')


def test_create_instance_manager_location_envvar(
        manager_location_envvar, instance_envvar, MMPClient, declared_ports):

    instance = Instance(declared_ports)
    instance.error_shutdown("")  # ensure all threads and resources are cleaned up

    MMPClient.assert_called_once_with(Ref('component[13]'), 'tcp:localhost:9002')


def test_create_instance_registration(
        manager_location_argv, instance_argv, mmp_client, communicator, port_manager,
        profiler, declared_ports):

    instance = Instance(declared_ports)
    instance.error_shutdown("")  # ensure all threads and resources are cleaned up

    locations = communicator.get_locations.return_value

    mmp_client.register_instance.assert_called_once()
    assert mmp_client.register_instance.call_args[0][0] == locations
    port_desc = mmp_client.register_instance.call_args[0][1]
    assert port_desc[0].name == 'in'
    assert port_desc[0].operator == Operator.F_INIT
    assert port_desc[1].name == 'not_connected'
    assert port_desc[1].operator == Operator.F_INIT
    assert port_desc[2].name == 'out_v'
    assert port_desc[2].operator == Operator.O_I
    assert port_desc[3].name == 'out_r'
    assert port_desc[3].operator == Operator.O_I
    assert port_desc[4].name == 'in_v'
    assert port_desc[4].operator == Operator.S
    assert port_desc[5].name == 'in_r'
    assert port_desc[5].operator == Operator.S
    assert port_desc[6].name == 'not_connected_v'
    assert port_desc[6].operator == Operator.S
    assert port_desc[7].name == 'out'
    assert port_desc[7].operator == Operator.O_F


def test_create_instance_profiling(
        manager_location_argv, instance_argv, profiler, declared_ports):

    instance = Instance(declared_ports)

    assert len(profiler.record_event.mock_calls) == 2
    instance.error_shutdown("Ensure all threads and resources are cleaned up")


def test_create_instance_connecting(
        manager_location_argv, instance_argv, mmp_client, port_manager, communicator,
        settings_manager, declared_ports):

    conduits = [MagicMock(), MagicMock()]
    peer_dims = {'component': [], 'other': []}
    peer_locations = {
            'component': ['tcp:localhost:9003'],
            'other': ['tcp:localhost:9004']}
    mmp_client.request_peers.return_value = (conduits, peer_dims, peer_locations)

    settings = MagicMock()
    mmp_client.get_settings.return_value = settings

    instance = Instance(declared_ports)

    port_manager.connect_ports.assert_called_once()
    peer_info = port_manager.connect_ports.call_args[0][0]
    assert peer_info._PeerInfo__kernel == Ref('component')
    assert peer_info._PeerInfo__index == []
    assert peer_info._PeerInfo__peer_dims == peer_dims
    assert peer_info._PeerInfo__peer_locations == peer_locations

    communicator.set_peer_info.assert_called_once()
    assert communicator.set_peer_info.call_args[0][0] == peer_info

    assert settings_manager.base == settings
    instance.error_shutdown("Ensure all threads and resources are cleaned up")


def test_create_instance_set_up_checkpointing(
        manager_location_argv, instance_argv, mmp_client, trigger_manager,
        no_resume_snapshot_manager, settings_manager, declared_ports):

    instance = Instance(declared_ports)

    elapsed_time, checkpoints, resume_path, snapshot_path = (
            mmp_client.get_checkpoint_info.return_value)

    trigger_manager.set_checkpoint_info.assert_called_with(elapsed_time, checkpoints)
    no_resume_snapshot_manager.prepare_resume.assert_called_with(
            resume_path, snapshot_path)
    assert settings_manager.overlay != no_resume_snapshot_manager.resume_overlay
    instance.error_shutdown("Ensure all threads and resources are cleaned up")


def test_create_instance_set_up_logging(
        manager_location_argv, instance_argv, settings_manager, declared_ports):

    def get_setting(instance, name, typ):
        return {
                'muscle_local_log_level': 'debug',
                'muscle_remote_log_level': 'error'}[str(name)]

    settings_manager.get_setting = get_setting

    root_logger = MagicMock()
    root_logger.isEnabledFor.return_value = False
    libmuscle_logger = MagicMock()
    ymmsl_logger = MagicMock()

    def get_logger(name=''):
        return {
                '': root_logger,
                'libmuscle': libmuscle_logger,
                'ymmsl': ymmsl_logger}[name]

    with patch('libmuscle.instance.logging.getLogger', get_logger):
        instance = Instance(declared_ports)

        assert instance._mmp_handler.level == logging.ERROR
        root_logger.setLevel.assert_called_with(logging.ERROR)
        libmuscle_logger.setLevel.assert_called_with(logging.DEBUG)
        ymmsl_logger.setLevel.assert_called_with(logging.DEBUG)
    instance.error_shutdown("Ensure all threads and resources are cleaned up")


def test_shutdown_instance(
        logger, instance, mmp_client, communicator, profiler):

    msg = 'Testing'
    num_profile_events = len(profiler.record_event.mock_calls)

    instance.error_shutdown(msg)

    logger.critical.assert_called_with(msg)
    communicator.shutdown.assert_called()

    mmp_client.deregister_instance.assert_called_once_with()
    mmp_client.close.assert_called_once_with()

    assert len(profiler.record_event.mock_calls) == num_profile_events + 1
    profiler.shutdown.assert_called_once_with()


def test_list_settings(instance, settings_manager):
    instance.list_settings()
    settings_manager.list_settings.assert_called_with(Ref('component'))


def test_get_setting(instance, settings_manager):
    settings_manager.get_setting.side_effect = None  # don't raise KeyError
    instance.get_setting('test', 'int')
    settings_manager.get_setting.assert_called_with(
            Ref('component'), Ref('test'), 'int')


def test_list_ports(instance, port_manager):
    port_manager.list_ports.assert_called_once_with()
    port_manager.list_ports.reset_mock()
    instance.list_ports()
    port_manager.list_ports.assert_called_once_with()


def test_is_connected(instance):
    assert instance.is_connected('in') is True
    assert instance.is_connected('not_connected') is False
    assert instance.is_connected('out_v') is True
    assert instance.is_connected('out_r') is True
    assert instance.is_connected('in_v') is True
    assert instance.is_connected('in_r') is True
    assert instance.is_connected('not_connected_v') is False
    assert instance.is_connected('out') is True


def test_is_vector_port(instance):
    assert instance.is_vector_port('in') is False
    assert instance.is_vector_port('not_connected') is False
    assert instance.is_vector_port('out_v') is True
    assert instance.is_vector_port('out_r') is True
    assert instance.is_vector_port('in_v') is True
    assert instance.is_vector_port('in_r') is True
    assert instance.is_vector_port('not_connected_v') is True
    assert instance.is_vector_port('out') is False


def test_is_resizable(instance):
    for port in ('in', 'not_connected', 'out_v', 'in_v', 'out'):
        assert instance.is_resizable(port) is False

    assert instance.is_resizable('out_r') is True
    assert instance.is_resizable('in_r') is True
    assert instance.is_resizable('not_connected_v') is True


def test_get_port_length(instance):
    assert instance.get_port_length('out_v') == 13
    assert instance.get_port_length('out_r') == 0
    assert instance.get_port_length('in_v') == 13
    assert instance.get_port_length('in_r') == 0


def test_set_port_length(instance, port_manager):
    instance.set_port_length('not_connected_v', 7)
    assert port_manager.get_port('not_connected_v').get_length() == 7


def test_reuse_set_overlay(
        instance, port_manager, mock_ports, communicator, settings_manager):
    port_manager.settings_in_connected.return_value = True
    mock_ports['in']._is_connected = False

    mock_msg = MagicMock()
    mock_msg.data = Settings({'s1': 1, 's2': 2})
    mock_msg.settings = Settings({'s0': 0})
    communicator.receive_message.return_value = mock_msg, 0.0

    instance.reuse_instance()

    communicator.receive_message.assert_called_with('muscle_settings_in')
    assert settings_manager.overlay['s0'] == 0
    assert settings_manager.overlay['s1'] == 1
    assert settings_manager.overlay['s2'] == 2


@pytest.mark.parametrize('closed_port', ['muscle_settings_in', 'in'])
def test_reuse_closed_port(instance, port_manager, communicator, closed_port):

    def receive_message(port, slot=None, default=None):
        mock_msg = MagicMock()
        if port == closed_port:
            mock_msg.data = ClosePort()
        else:
            mock_msg.data = Settings()
        return mock_msg, 0.0

    port_manager.settings_in_connected.return_value = True
    communicator.receive_message = receive_message

    assert instance.reuse_instance() is False


def test_reuse_f_init_vector_port(instance, port_manager, communicator):
    port_manager.get_port('in')._length = 10

    def receive_message(port, slot=None, default=None):
        mock_msg = MagicMock()
        mock_msg.data = Settings()
        return mock_msg, 0.0

    communicator.receive_message = receive_message

    assert instance.reuse_instance() is True


def test_reuse_no_f_init_ports(instance, connected_port_manager, communicator):
    connected_port_manager.list_ports.return_value = {}

    assert instance.reuse_instance() is True
    assert instance.reuse_instance() is False


def test_send_message(instance, settings_manager, communicator):
    port = 'out_v'
    msg = MagicMock()
    msg.settings = None
    slot = 3

    instance.send(port, msg, slot)

    communicator.send_message.assert_called_once()
    args = communicator.send_message.call_args[0]
    assert args[0] == port
    assert args[1].settings == settings_manager.overlay
    assert args[2] == slot


def test_send_on_invalid_port(instance):
    with pytest.raises(RuntimeError):
        instance.send('does_not_exist', MagicMock())


def test_send_after_resize(instance, message):
    with pytest.raises(RuntimeError):
        instance.send('out_r', message, 13)

    instance.set_port_length('out_r', 20)
    instance.send('out_r', message, 13)


def test_send_on_receiving_port(instance, message):
    with pytest.raises(RuntimeError):
        instance.send("in_v", message, 3)


def test_receive_on_invalid_port(instance):
    with pytest.raises(RuntimeError):
        instance.receive('does_not_exist')


def test_receive_on_sending_port(instance):
    with pytest.raises(RuntimeError):
        instance.receive("out_v", 3)


def test_receive_f_init(instance, port_manager, communicator):
    mock_msg = MagicMock()
    mock_msg.data = Settings()
    communicator.receive_message.return_value = mock_msg, 0.0

    instance.reuse_instance()

    msg = instance.receive('in')

    assert msg == mock_msg


def test_receive_default_f_init(instance):
    default_msg = MagicMock()

    msg = instance.receive('not_connected', default=default_msg)

    assert msg == default_msg


def test_receive_default(instance):
    default_msg = MagicMock()

    msg = instance.receive('not_connected_v', 42, default_msg)

    assert msg == default_msg


def test_receive_no_default(instance):
    with pytest.raises(RuntimeError):
        instance.receive('not_connected')

    with pytest.raises(RuntimeError):
        instance.receive('not_connected_v', 14)


def test_receive_inconsistent_settings(
        instance, settings_manager, port_manager, communicator):

    def receive_message(port, slot=None):
        mock_msg = MagicMock()
        if port == 'muscle_settings_in':
            mock_msg.data = Settings({'s1': 1})
            mock_msg.settings = Settings()
        else:
            mock_msg.data = None
            mock_msg.settings = Settings({'s0': 0})
        return mock_msg, 0.0

    communicator.receive_message.side_effect = receive_message

    port_manager.settings_in_connected.return_value = True

    with pytest.raises(RuntimeError):
        instance.reuse_instance()


def test_receive_with_settings(
        instance_dont_apply_overlay, settings_manager, communicator):

    mock_msg = MagicMock()
    mock_msg.settings = Settings({'s0': 0, 's1': 1})
    communicator.receive_message.return_value = mock_msg, 0.0

    instance_dont_apply_overlay.reuse_instance()
    msg = instance_dont_apply_overlay.receive('in')

    assert msg.settings['s0'] == 0
    assert msg.settings['s1'] == 1

    assert len(settings_manager.overlay) == 0


def test_receive_with_settings_default(
        instance_dont_apply_overlay, settings_manager, port_manager, communicator):

    port_manager.get_port('in')._is_connected = False

    instance_dont_apply_overlay.reuse_instance()

    default_msg = MagicMock()
    default_msg.settings = MagicMock()
    msg = instance_dont_apply_overlay.receive('in', default=default_msg)

    assert msg == default_msg
    assert msg.settings == default_msg.settings
    assert len(settings_manager.overlay) == 0


@pytest.mark.parametrize('flags, expectation', [
        (InstanceFlags(0), pytest.raises(RuntimeError)),
        (InstanceFlags.USES_CHECKPOINT_API, does_not_raise()),
        (InstanceFlags.KEEPS_NO_STATE_FOR_NEXT_USE, does_not_raise()),
        (InstanceFlags.STATE_NOT_REQUIRED_FOR_NEXT_USE, does_not_raise())])
def test_checkpoint_support(
        instance_argv, mmp_client, tmp_path, flags, expectation):

    checkpoint_info = (0.0, Checkpoints(at_end=True), None, tmp_path)
    mmp_client.get_checkpoint_info.return_value = checkpoint_info

    with expectation:
        instance = Instance(flags=flags)
        instance.error_shutdown("Ensure all threads and resources are cleaned up")
