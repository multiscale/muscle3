from typing import List

import grpc
from ymmsl import Endpoint, Reference

import libmuscle.manager_protocol.muscle_manager_protocol_pb2 as mmp
import libmuscle.manager_protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc

from libmuscle.endpoint import endpoint_to_grpc
from libmuscle.logging import LogMessage


class MMPClient():
    """The client for the MUSCLE Manager Protocol.

    This class connects to the Manager and communicates with it on \
    behalf of the rest of libmuscle.

    It manages the connection, and converts between our native types \
    and the gRPC generated types.
    """
    def __init__(self) -> None:
        channel = grpc.insecure_channel('localhost:9000')
        self.__client = mmp_grpc.MuscleManagerStub(channel)

    def submit_log_message(self, message: LogMessage) -> None:
        self.__client.SubmitLogMessage(message.to_grpc())

    def register_instance(self, name: Reference, location: str,
                          endpoints: List[Endpoint]) -> None:
        grpc_endpoints = list(map(endpoint_to_grpc, endpoints))
        request = mmp.RegistrationRequest(
                instance_name=str(name),
                network_location=location,
                endpoints=grpc_endpoints)
        self.__client.RegisterInstance(request)
