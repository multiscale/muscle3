from ymmsl import Endpoint, Reference

from libmuscle.operator import operator_from_grpc, operator_to_grpc

import muscle_manager.protocol.muscle_manager_protocol_pb2 as mmp


def endpoint_from_grpc(endpoint: mmp.Endpoint) -> Endpoint:
    return Endpoint(
            Reference.from_string(endpoint.name),
            operator_from_grpc(endpoint.operator))


def endpoint_to_grpc(endpoint: Endpoint) -> mmp.Endpoint:
    return mmp.Endpoint(
            name=str(endpoint.name),
            operator=operator_to_grpc(endpoint.operator))
