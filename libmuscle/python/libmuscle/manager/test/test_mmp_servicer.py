from google.protobuf.timestamp_pb2 import Timestamp
from ymmsl import Operator

from libmuscle.manager.mmp_server import MMPServicer
import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


def test_create_servicer(logger, settings, instance_registry,
                         topology_store):
    MMPServicer(logger, settings, instance_registry, topology_store)


def test_log_message(mmp_servicer, caplog):
    timestamp = Timestamp()
    timestamp.FromJsonString("1970-01-01T00:00:00.000Z")
    message = mmp.LogMessage(
            instance_id='test_instance_id',
            timestamp=timestamp,
            level=mmp.LOG_LEVEL_WARNING,
            text='Testing log message')
    result = mmp_servicer.SubmitLogMessage(message, None)
    assert isinstance(result, mmp.LogResult)
    assert caplog.records[0].name == 'instances.test_instance_id'
    assert caplog.records[0].time_stamp == '1970-01-01T00:00:00Z'
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == (
            'Testing log message')


def test_request_settings(settings, mmp_servicer):
    request = mmp.SettingsRequest()
    result = mmp_servicer.RequestSettings(request, None)

    assert len(result.setting_values) == 0

    settings['test1'] = 13
    settings['test2'] = 12.3
    settings['test3'] = 'testing'
    settings['test4'] = True
    settings['test5'] = [2.3, 7.4]
    settings['test6'] = [[1.0, 2.0], [2.0, 1.0]]

    result = mmp_servicer.RequestSettings(request, None)
    assert len(result.setting_values) == 6

    result_dict = dict()
    for mmp_setting in result.setting_values:
        result_dict[mmp_setting.name] = (
                mmp_setting.value_type, mmp_setting.value_string,
                mmp_setting.value_int, mmp_setting.value_float,
                mmp_setting.value_bool, mmp_setting.value_list_float,
                mmp_setting.value_list_list_float)

    no_list = mmp.ListOfDouble()
    no_list2 = mmp.ListOfListOfDouble()
    assert result_dict['test1'] == (
            mmp.SETTING_VALUE_TYPE_INT, '', 13, 0.0, False, no_list,
            no_list2)
    assert result_dict['test2'] == (
            mmp.SETTING_VALUE_TYPE_FLOAT, '', 0, 12.3, False, no_list,
            no_list2)
    assert result_dict['test3'] == (
            mmp.SETTING_VALUE_TYPE_STRING, 'testing', 0, 0.0, False, no_list,
            no_list2)
    assert result_dict['test4'] == (
            mmp.SETTING_VALUE_TYPE_BOOL, '', 0, 0.0, True, no_list, no_list2)
    assert result_dict['test5'] == (
            mmp.SETTING_VALUE_TYPE_LIST_FLOAT, '', 0, 0.0, False,
            mmp.ListOfDouble(values=[2.3, 7.4]), no_list2)
    row0 = mmp.ListOfDouble(values=[1.0, 2.0])
    row1 = mmp.ListOfDouble(values=[2.0, 1.0])
    assert result_dict['test6'] == (
            mmp.SETTING_VALUE_TYPE_LIST_LIST_FLOAT, '', 0, 0.0, False,
            no_list, mmp.ListOfListOfDouble(values=[row0, row1]))


def test_register_instance(mmp_servicer, instance_registry):
    port = mmp.Port(name='test_in', operator=mmp.OPERATOR_F_INIT)
    request = mmp.RegistrationRequest(
            instance_name='test_instance',
            network_locations=['tcp://localhost:10000'],
            ports=[port])

    result = mmp_servicer.RegisterInstance(request, None)

    assert result.status == mmp.RESULT_STATUS_SUCCESS
    assert (instance_registry._InstanceRegistry__locations['test_instance'] ==
            ['tcp://localhost:10000'])

    registered_ports = instance_registry._InstanceRegistry__ports
    assert registered_ports['test_instance'][0].name == 'test_in'
    assert registered_ports['test_instance'][0].operator == Operator.F_INIT


def test_double_register_instance(mmp_servicer, instance_registry):
    port = mmp.Port(name='test_in', operator=mmp.OPERATOR_F_INIT)
    request = mmp.RegistrationRequest(
            instance_name='test_instance',
            network_locations=['tcp://localhost:10000'],
            ports=[port])

    result = mmp_servicer.RegisterInstance(request, None)
    assert result.status == mmp.RESULT_STATUS_SUCCESS

    result = mmp_servicer.RegisterInstance(request, None)
    assert result.status == mmp.RESULT_STATUS_ERROR
    assert 'test_instance' in result.error_message


def test_request_peers_pending(mmp_servicer):
    request = mmp.PeerRequest(instance_name='micro[0][0]')
    result = mmp_servicer.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_PENDING


def test_request_peers_fanout(registered_mmp_servicer):
    request = mmp.PeerRequest(instance_name='macro')
    result = registered_mmp_servicer.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_SUCCESS

    assert result.conduits[0] == mmp.Conduit(
            sender='macro.out', receiver='micro.in')
    assert result.conduits[1] == mmp.Conduit(
            sender='micro.out', receiver='macro.in')

    assert result.peer_dimensions[0] == mmp.PeerResult.PeerDimensions(
            peer_name='micro', dimensions=[10, 10])

    for i, peer_locations in enumerate(result.peer_locations):
        instance = 'micro[{}][{}]'.format(i // 10, i % 10)
        location = 'direct:{}'.format(instance)
        assert peer_locations == mmp.PeerResult.PeerLocations(
                instance_name=instance, locations=[location])


def test_request_peers_fanin(registered_mmp_servicer):
    request = mmp.PeerRequest(instance_name='micro[4][3]')
    result = registered_mmp_servicer.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_SUCCESS

    assert result.conduits[0] == mmp.Conduit(
            sender='macro.out', receiver='micro.in')
    assert result.conduits[1] == mmp.Conduit(
            sender='micro.out', receiver='macro.in')

    assert result.peer_dimensions[0] == mmp.PeerResult.PeerDimensions(
            peer_name='macro', dimensions=[])

    assert result.peer_locations[0] == mmp.PeerResult.PeerLocations(
            instance_name='macro', locations=['direct:macro'])


def test_request_peers_bidir(registered_mmp_servicer2):
    request = mmp.PeerRequest(instance_name='meso[2]')
    result = registered_mmp_servicer2.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_SUCCESS

    assert result.conduits[0] == mmp.Conduit(
            sender='macro.out', receiver='meso.in')
    assert result.conduits[1] == mmp.Conduit(
            sender='meso.out', receiver='micro.in')
    assert result.conduits[2] == mmp.Conduit(
            sender='micro.out', receiver='meso.in')
    assert result.conduits[3] == mmp.Conduit(
            sender='meso.out', receiver='macro.in')

    assert mmp.PeerResult.PeerDimensions(
            peer_name='micro', dimensions=[5, 10]) in result.peer_dimensions
    assert mmp.PeerResult.PeerDimensions(
            peer_name='macro', dimensions=[]) in result.peer_dimensions

    assert mmp.PeerResult.PeerLocations(
            instance_name='macro',
            locations=['direct:macro']) in result.peer_locations

    for i in range(10):
        instance = 'micro[2][{}]'.format(i)
        location = 'direct:{}'.format(instance)
        assert mmp.PeerResult.PeerLocations(
                instance_name=instance,
                locations=[location]) in result.peer_locations


def test_request_peers_own_conduits(registered_mmp_servicer2):
    request = mmp.PeerRequest(instance_name='macro')
    result = registered_mmp_servicer2.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_SUCCESS

    assert result.conduits[0] == mmp.Conduit(
            sender='macro.out', receiver='meso.in')
    assert result.conduits[1] == mmp.Conduit(
            sender='meso.out', receiver='macro.in')


def test_request_peers_unknown(registered_mmp_servicer2):
    request = mmp.PeerRequest(instance_name='does_not_exist')
    result = registered_mmp_servicer2.RequestPeers(request, None)
    assert result.status == mmp.RESULT_STATUS_ERROR
    assert result.error_message is not None
    assert 'does_not_exist' in result.error_message
