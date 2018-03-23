import grpc

import libmuscle.manager_protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc

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
