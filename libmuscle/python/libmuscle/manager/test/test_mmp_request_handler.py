import msgpack
from ymmsl import Operator, Reference

from libmuscle.logging import LogLevel
from libmuscle.manager.mmp_server import MMPRequestHandler
from libmuscle.mcp.protocol import RequestType, ResponseType


def test_create_servicer(logger, settings, instance_registry,
                         topology_store):
    MMPRequestHandler(logger, settings, instance_registry, topology_store)


def test_log_message(mmp_request_handler, caplog):
    request = [
            RequestType.SUBMIT_LOG_MESSAGE.value,
            'test_instance_id', 0.0, LogLevel.WARNING.value,
            'Testing log message']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = mmp_request_handler.handle_request(encoded_request)

    decoded_result = msgpack.unpackb(result, raw=False)

    assert isinstance(decoded_result, list)
    assert len(decoded_result) == 1
    assert decoded_result[0] == ResponseType.SUCCESS.value

    assert caplog.records[0].name == 'test_instance_id'
    assert caplog.records[0].levelname == 'WARNING'
    assert caplog.records[0].message == 'Testing log message'


def test_get_settings(settings, mmp_request_handler):
    request = [RequestType.GET_SETTINGS.value]
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert len(decoded_result) == 2
    assert decoded_result[0] == ResponseType.SUCCESS.value
    assert decoded_result[1] == {}

    settings['test1'] = 13
    settings['test2'] = 12.3
    settings['test3'] = 'testing'
    settings['test4'] = True
    settings['test5'] = [2.3, 7.4]
    settings['test6'] = [[1.0, 2.0], [2.0, 1.0]]

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)
    assert len(decoded_result) == 2
    assert decoded_result[0] == ResponseType.SUCCESS.value

    result_dict = decoded_result[1]
    assert len(result_dict) == 6

    assert result_dict['test1'] == 13
    assert result_dict['test2'] == 12.3
    assert result_dict['test3'] == 'testing'
    assert result_dict['test4'] is True
    assert result_dict['test5'] == [2.3, 7.4]
    assert result_dict['test6'] == [[1.0, 2.0], [2.0, 1.0]]
    assert result_dict == settings.as_ordered_dict()


def test_register_instance(mmp_request_handler, instance_registry):
    request = [
            RequestType.REGISTER_INSTANCE.value,
            'test_instance',
            ['tcp://localhost:10000'],
            [['test_in', 'F_INIT']]]
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.SUCCESS.value
    assert (instance_registry._locations['test_instance'] ==
            ['tcp://localhost:10000'])

    registered_ports = instance_registry._ports
    assert registered_ports['test_instance'][0].name == 'test_in'
    assert registered_ports['test_instance'][0].operator == Operator.F_INIT


def test_double_register_instance(mmp_request_handler):
    request = [
            RequestType.REGISTER_INSTANCE.value,
            'test_instance',
            ['tcp://localhost:10000'],
            [['test_in', 'F_INIT']]]
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.SUCCESS.value

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.ERROR.value
    assert 'test_instance' in decoded_result[1]


def test_deregister_instance(
        registered_mmp_request_handler, instance_registry):
    assert Reference('macro') in instance_registry._locations

    request = [RequestType.DEREGISTER_INSTANCE.value, 'macro']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.SUCCESS.value
    assert Reference('macro') not in instance_registry._locations


def test_get_peers_pending(mmp_request_handler):
    request = [RequestType.GET_PEERS.value, 'micro[0][0]']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.PENDING.value


def test_request_peers_fanout(registered_mmp_request_handler):
    request = [RequestType.GET_PEERS.value, 'macro']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    status, conduits, dims, locations = decoded_result
    assert status == ResponseType.SUCCESS.value

    assert conduits[0][0] == 'macro.out'
    assert conduits[0][1] == 'micro.in'
    assert conduits[1][0] == 'micro.out'
    assert conduits[1][1] == 'macro.in'

    assert dims['micro'] == [10, 10]

    for i, (name, locs) in enumerate(locations.items()):
        assert name == f'micro[{i // 10}][{i % 10}]'
        assert locs == [f'direct:{name}']


def test_request_peers_fanin(registered_mmp_request_handler):
    request = [RequestType.GET_PEERS.value, 'micro[4][3]']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    status, conduits, dims, locations = decoded_result
    assert status == ResponseType.SUCCESS.value

    assert conduits[0][0] == 'macro.out'
    assert conduits[0][1] == 'micro.in'
    assert conduits[1][0] == 'micro.out'
    assert conduits[1][1] == 'macro.in'

    assert dims['macro'] == []

    assert locations['macro'] == ['direct:macro']


def test_request_peers_bidir(registered_mmp_request_handler2):
    request = [RequestType.GET_PEERS.value, 'meso[2]']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler2.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    status, conduits, dims, locations = decoded_result
    assert status == ResponseType.SUCCESS.value

    assert conduits[0][0] == 'macro.out'
    assert conduits[0][1] == 'meso.in'
    assert conduits[1][0] == 'meso.out'
    assert conduits[1][1] == 'micro.in'
    assert conduits[2][0] == 'micro.out'
    assert conduits[2][1] == 'meso.in'
    assert conduits[3][0] == 'meso.out'
    assert conduits[3][1] == 'macro.in'

    assert dims['micro'] == [5, 10]
    assert dims['macro'] == []

    assert locations['macro'] == ['direct:macro']

    assert locations['macro'] == ['direct:macro']
    for i in range(10):
        assert locations[f'micro[2][{i}]'] == [f'direct:micro[2][{i}]']


def test_request_peers_own_conduits(registered_mmp_request_handler2):
    request = [RequestType.GET_PEERS.value, 'macro']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler2.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    status, conduits, dims, locations = decoded_result
    assert status == ResponseType.SUCCESS.value

    assert conduits[0][0] == 'macro.out'
    assert conduits[0][1] == 'meso.in'
    assert conduits[1][0] == 'meso.out'
    assert conduits[1][1] == 'macro.in'


def test_request_peers_unknown(registered_mmp_request_handler2):
    request = [RequestType.GET_PEERS.value, 'does_not_exist']
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = registered_mmp_request_handler2.handle_request(encoded_request)
    decoded_result = msgpack.unpackb(result, raw=False)

    status, error_msg = decoded_result
    assert status == ResponseType.ERROR.value
    assert error_msg is not None
    assert 'does_not_exist' in error_msg
