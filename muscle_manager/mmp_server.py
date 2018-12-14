from concurrent import futures

import grpc
from ymmsl import Reference

from libmuscle.port import port_from_grpc
from libmuscle.logging import LogLevel, Timestamp
from libmuscle.operator import operator_from_grpc

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp
import muscle_manager_protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc


class MMPServicer(mmp_grpc.MuscleManagerServicer):
    """The MUSCLE Manager Protocol server.

    This class handles incoming requests from the instances comprising \
    the multiscale simulation to be executed.

    Args:
        logger: The Logger component to log messages to.
    """
    def __init__(
            self,
            logger: Logger,
            instance_registry: InstanceRegistry
            ) -> None:
        self.__logger = logger
        self.__instance_registry = instance_registry

    def SubmitLogMessage(
            self,
            request: mmp.LogMessage,
            context: grpc.ServicerContext
            ) -> mmp.LogResult:
        """Forwards a submitted log message to the Logger."""
        self.__logger.log_message(
                request.instance_id,
                operator_from_grpc(request.operator),
                Timestamp.from_grpc(request.timestamp),
                LogLevel.from_grpc(request.level),
                request.text)
        return mmp.LogResult()

    def RegisterInstance(
            self,
            request: mmp.RegistrationRequest,
            context: grpc.ServicerContext
            ) -> mmp.RegistrationResult:
        """Handles an instance registration request."""
        try:
            ports = list(map(port_from_grpc, request.ports))
            self.__instance_registry.add(
                    Reference(str(request.instance_name)),
                    list(request.network_locations),
                    ports)
            return mmp.RegistrationResult(status=mmp.RESULT_STATUS_SUCCESS)
        except ValueError as e:
            return mmp.RegistrationResult(
                    status=mmp.RESULT_STATUS_ERROR,
                    error_message=('An instance with name {} was already'
                                   ' registered').format(
                                           request.instance_name))


class MMPServer():
    """The MUSCLE Manager Protocol server.

    This class accepts connections from the instances comprising \
    the multiscale model to be executed, and services them using an \
    MMPServicer.
    """
    def __init__(
            self,
            logger: Logger,
            instance_registry: InstanceRegistry
            ) -> None:
        self.__servicer = MMPServicer(logger, instance_registry)
        self.__server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
        mmp_grpc.add_MuscleManagerServicer_to_server(  # type: ignore
                self.__servicer, self.__server)
        self.__server.add_insecure_port('[::]:9000')
        self.__server.start()

    def stop(self) -> None:
        self.__server.stop(0)
