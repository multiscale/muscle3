from concurrent import futures
from typing import cast, Generator, List

import grpc
from ymmsl import Reference

from libmuscle.configuration import Configuration
from libmuscle.port import port_from_grpc
from libmuscle.logging import LogLevel, Timestamp
from libmuscle.operator import operator_from_grpc
from libmuscle.util import (conduit_to_grpc, instance_indices,
                            instance_to_kernel)

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.topology_store import TopologyStore

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
            configuration: Configuration,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore
            ) -> None:
        self.__logger = logger
        self.__configuration = configuration
        self.__instance_registry = instance_registry
        self.__topology_store = topology_store

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

    def RequestConfiguration(
            self,
            request: mmp.ConfigurationRequest,
            context: grpc.ServicerContext
            ) -> mmp.ConfigurationResult:
        """Returns the central base configuration."""
        settings = list()   # type: List[mmp.Setting]
        for parameter, value in self.__configuration.items():
            if isinstance(value, str):
                setting = mmp.Setting(
                        parameter=str(parameter),
                        value_type=mmp.PARAMETER_VALUE_TYPE_STRING,
                        value_string=value)
            elif isinstance(value, bool):
                # a bool is an int in Python, so this needs to go before the
                # branch for int
                setting = mmp.Setting(
                        parameter=str(parameter),
                        value_type=mmp.PARAMETER_VALUE_TYPE_BOOL,
                        value_bool=value)
            elif isinstance(value, int):
                setting = mmp.Setting(
                        parameter=str(parameter),
                        value_type=mmp.PARAMETER_VALUE_TYPE_INT,
                        value_int=value)
            elif isinstance(value, float):
                setting = mmp.Setting(
                        parameter=str(parameter),
                        value_type=mmp.PARAMETER_VALUE_TYPE_FLOAT,
                        value_float=value)
            elif isinstance(value, list):
                if len(value) == 0 or isinstance(value[0], float):
                    value = cast(List[float], value)
                    mmp_values = mmp.ListOfDouble(values=value)
                    setting = mmp.Setting(
                            parameter=str(parameter),
                            value_type=mmp.PARAMETER_VALUE_TYPE_LIST_FLOAT,
                            value_list_float=mmp_values)
                elif isinstance(value[0], list):
                    value = cast(List[List[float]], value)
                    rows = list()
                    for row in value:
                        mmp_row = mmp.ListOfDouble(values=row)
                        rows.append(mmp_row)
                    mmp_rows = mmp.ListOfListOfDouble(values=rows)

                    LLF = mmp.PARAMETER_VALUE_TYPE_LIST_LIST_FLOAT
                    setting = mmp.Setting(
                            parameter=str(parameter),
                            value_type=LLF,
                            value_list_list_float=mmp_rows)
            settings.append(setting)

        return mmp.ConfigurationResult(parameter_values=settings)

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

    def RequestPeers(
            self,
            request: mmp.PeerRequest,
            context: grpc.ServicerContext
            ) -> mmp.PeerResult:
        """Handles a peer request."""
        # get info from yMMSL
        instance = Reference(request.instance_name)
        kernel = instance_to_kernel(instance)
        if not self.__topology_store.has_kernel(kernel):
            return mmp.PeerResult(status=mmp.RESULT_STATUS_ERROR,
                                  error_message='Unknown kernel {}'.format(
                                      kernel))

        conduits = self.__topology_store.get_conduits(kernel)
        mmp_conduits = [conduit_to_grpc(c) for c in conduits]

        peer_dims = self.__topology_store.get_peer_dimensions(kernel)
        mmp_dimensions = [
                mmp.PeerResult.PeerDimensions(peer_name=str(name),
                                              dimensions=dims)
                for name, dims in peer_dims.items()]

        # generate instances
        peer_instances = self.__generate_peer_instances(instance)
        try:
            instance_locations = [
                    mmp.PeerResult.PeerLocations(
                        instance_name=str(instance),
                        locations=self.__instance_registry.get_locations(
                            instance))
                    for instance in peer_instances]
        except KeyError as e:
            return mmp.PeerResult(status=mmp.RESULT_STATUS_PENDING,
                                  error_message='Waiting for kernel {}'.format(
                                      e.args[0]))

        return mmp.PeerResult(
                status=mmp.RESULT_STATUS_SUCCESS,
                conduits=mmp_conduits,
                peer_dimensions=mmp_dimensions,
                peer_locations=instance_locations)

    def __generate_peer_instances(self, instance: Reference
                                  ) -> Generator[Reference, None, None]:
        """Generates the names of all peer instances of an instance.

        Args:
            instance: The instance whose peers to generate.

        Yields:
            All peer instance identifiers.
        """
        kernel = instance_to_kernel(instance)
        indices = instance_indices(instance)
        dims = self.__topology_store.kernel_dimensions[kernel]
        all_peer_dims = self.__topology_store.get_peer_dimensions(kernel)
        for peer, peer_dims in all_peer_dims.items():
            base = peer
            for i in range(min(len(dims), len(peer_dims))):
                base += indices[i]

            if dims >= peer_dims:
                yield base
            else:

                for peer_indices in self.__generate_indices(
                        peer_dims[len(dims):]):
                    yield base + peer_indices

    def __generate_indices(self, dims: List[int]
                           ) -> Generator[List[int], None, None]:
        """Generates all indices in a block of the given dimensions.

        Args:
            dims: The dimensions of the block.

        Yields:
            Lists of indices, one for each point in the block.
        """
        index = [0] * len(dims)
        done = False
        while not done:
            yield index
            done = self.__increment_index(index, dims)

    def __increment_index(self, index: List[int], dims: List[int]) -> bool:
        """Increments an index.

        Args:
            index: The index to be incremented.
            dims: The dimensions of the block this index is in.

        Returns:
            True iff the index overflowed and is now all zeros again.
        """
        cur = len(index) - 1
        index[cur] += 1
        while index[cur] == dims[cur]:
            index[cur] = 0
            if cur == 0:
                return True
            cur -= 1
            index[cur] += 1
        return False


class MMPServer():
    """The MUSCLE Manager Protocol server.

    This class accepts connections from the instances comprising \
    the multiscale model to be executed, and services them using an \
    MMPServicer.
    """
    def __init__(
            self,
            logger: Logger,
            configuration: Configuration,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore
            ) -> None:
        self.__servicer = MMPServicer(logger, configuration, instance_registry,
                                      topology_store)
        self.__server = grpc.server(futures.ThreadPoolExecutor())
        mmp_grpc.add_MuscleManagerServicer_to_server(  # type: ignore
                self.__servicer, self.__server)
        self.__server.add_insecure_port('[::]:9000')
        self.__server.start()

    def stop(self) -> None:
        self.__server.stop(0)
