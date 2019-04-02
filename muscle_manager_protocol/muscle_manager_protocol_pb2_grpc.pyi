import grpc

from muscle_manager_protocol.muscle_manager_protocol_pb2 import (
        ConfigurationRequest, ConfigurationResult, LogMessage, LogResult,
        Profile, ProfileResult, RegistrationRequest, RegistrationResult,
        DeregistrationRequest, DeregistrationResult)


class MuscleManagerStub():
    def __init__(self, channel: grpc.Channel) -> None: ...

    def SubmitLogMessage(self, request: LogMessage) -> LogResult: ...

    def SubmitProfileEvents(self, request: Profile) -> ProfileResult: ...

    def RequestConfiguration(self, request: ConfigurationRequest
                             ) -> ConfigurationResult: ...

    def RegisterInstance(self, request: RegistrationRequest
                         ) -> RegistrationResult: ...

    def RequestPeers(self, request: PeerRequest) -> PeerResult: ...

    def DeregisterInstance(self, request: DeregistrationRequest
                           ) -> DeregistrationResult: ...


class MuscleManagerServicer():
    def __init__(self, **args) -> None: ...

    def SubmitLogMessage(self, request: LogMessage,
                         context: grpc.ServicerContext) -> LogResult: ...

    def SubmitProfileEvents(self, request: Profile,
                            context: grpc.ServicerContext
                            ) -> ProfileResult: ...

    def RequestConfiguration(self, request: ConfigurationRequest,
                             context: grpc.ServicerContext
                             ) -> ConfigurationResult: ...

    def RegisterInstance(self, request: RegistrationRequest,
                         context: grpc.ServicerContext
                         ) -> RegistrationResult: ...

    def RequestPeers(self, request: PeerRequest, context: grpc.ServicerContext
                     ) -> PeerResult: ...

    def DeregisterInstance(self, request: DeregistrationRequest,
                           context: grpc.ServicerContext
                           ) -> DeregistrationResult: ...
