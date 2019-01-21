import grpc

from muscle_manager_protocol.muscle_manager_protocol_pb2 import (
        ConfigurationRequest, ConfigurationResult, LogMessage, LogResult,
        RegistrationRequest, RegistrationResult)


class MuscleManagerStub():
    def __init__(self, channel: grpc.Channel) -> None: ...

    def SubmitLogMessage(self, request: LogMessage) -> LogResult: ...

    def RequestConfiguration(self, request: ConfigurationRequest
                             ) -> ConfigurationResult: ...

    def RegisterInstance(self, request: RegistrationRequest
                         ) -> RegistrationResult: ...

    def RequestPeers(self, request: PeerRequest) -> PeerResult: ...


class MuscleManagerServicer():
    def __init__(self, **args) -> None: ...

    def SubmitLogMessage(self, request: LogMessage,
                         context: grpc.ServicerContext) -> LogResult: ...

    def RequestConfiguration(self, request: ConfigurationRequest,
                             context: grpc.ServicerContext
                             ) -> ConfigurationResult: ...

    def RegisterInstance(self, request: RegistrationRequest,
                         context: grpc.ServicerContext
                         ) -> RegistrationResult: ...

    def RequestPeers(self, request: PeerRequest, context: grpc.ServicerContext
                     ) -> PeerResult: ...
