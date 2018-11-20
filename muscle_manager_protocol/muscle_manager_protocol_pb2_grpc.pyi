import grpc

from muscle_manager_protocol.muscle_manager_protocol_pb2 import (
        LogMessage, LogResult, RegistrationRequest, RegistrationResult)


class MuscleManagerStub():
    def __init__(self, channel: grpc.Channel) -> None: ...

    def SubmitLogMessage(self, request: LogMessage) -> LogResult: ...

    def RegisterInstance(self, request: RegistrationRequest
                         ) -> RegistrationResult: ...


class MuscleManagerServicer():
    def __init__(self, **args) -> None: ...

    def SubmitLogMessage(self, request: LogMessage,
                         context: grpc.ServicerContext) -> LogResult: ...

    def RegisterInstance(self, request: RegistrationRequest,
                         context: grpc.ServicerContext
                         ) -> RegistrationResult: ...
