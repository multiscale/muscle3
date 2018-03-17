import os
import sys
from typing import Any, Dict

import grpc

from muscle_manager.logger import Logger, LogLevel
from muscle_manager.operator import Operator
from muscle_manager.grpc_support import operator_from_grpc, log_level_from_grpc
import muscle_manager.protocol.muscle_manager_protocol_pb2 as mmp
import muscle_manager.protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc


class MMPServer(mmp_grpc.MuscleManagerServicer):
    """The MUSCLE Manager Protocol server.

    This class handles incoming requests from the instances comprising \
    the multiscale simulation to be executed.

    Args:
        logger: The Logger component to log messages to.
    """
    def __init__(
            self,
            logger: Logger
            ) -> None:
        self.__logger = logger

    def SubmitLogMessage(
            self,
            request: mmp.LogMessage,
            context: grpc.ServicerContext
            ) -> mmp.LogResult:

        self.__logger.log_message(
                request.instance_id,
                operator_from_grpc(request.operator),
                request.timestamp,
                log_level_from_grpc(request.level),
                request.text)
