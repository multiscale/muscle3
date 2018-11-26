from typing import Optional

from ymmsl import Identifier, Operator, Port, Reference

from libmuscle.operator import operator_from_grpc, operator_to_grpc
import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


# Convert between grpc and ymmsl Port types
def port_from_grpc(port: mmp.Port) -> Port:
    return Port(
            Identifier(port.name),
            operator_from_grpc(port.operator))


def port_to_grpc(port: Port) -> mmp.Port:
    return mmp.Port(
            name=str(port.name),
            operator=operator_to_grpc(port.operator))
