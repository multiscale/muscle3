import msgpack
from ymmsl import Reference

from libmuscle.logging import LogLevel
from libmuscle.manager.mlp_server import MLPRequestHandler
from libmuscle.mcp.protocol import RequestType, ResponseType


def test_create_servicer(logger, profile_store):
    MLPRequestHandler(logger, profile_store)


def test_report_usage(logger, profile_store):
    profile_store.store_instances([Reference('instance1'),Reference('instance2'),Reference('instance3')])
    handler = MLPRequestHandler(logger, profile_store)

    usage = {
            "instance1": (0.1, 1024),
            "instance2": (0.2, 2048),
            "instance3": (0.3, 3072),
            }

    request = [
            RequestType.REPORT_USAGE.value,
            "node_name0", usage]
    encoded_request = msgpack.packb(request, use_bin_type=True)

    result = handler.handle_request(encoded_request)

    decoded_result = msgpack.unpackb(result, raw=False)

    assert decoded_result[0] == ResponseType.SUCCESS.value