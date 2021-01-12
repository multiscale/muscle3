from concurrent import futures
import time
import socket
from typing import cast, Generator, List

import grpc
from ymmsl import Reference, Settings

from libmuscle.port import port_from_grpc
from libmuscle.logging import LogLevel, Timestamp
from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.util import (conduit_to_grpc, generate_indices,
                            instance_indices, instance_to_kernel)

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp
import muscle_manager_protocol.muscle_manager_protocol_pb2_grpc as mmp_grpc


class MMPServicer(mmp_grpc.MuscleManagerServicer):
    """The MUSCLE Manager Protocol server.

    This class handles incoming requests from the instances comprising \
    the multiscale simulation to be executed.

    Args:
        logger: The Logger component to log messages to.
        settings: The global settings to serve to instances.
        instance_registry: The database for instances.
        topology_store: Keeps track of how to connect things.
    """
    def __init__(
            self,
            logger: Logger,
            settings: Settings,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore
            ) -> None:
        self.__logger = logger
        self.__settings = settings
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
                Timestamp.from_grpc(request.timestamp),
                LogLevel.from_grpc(request.level),
                request.text)
        return mmp.LogResult()

    def SubmitProfileEvents(
            self,
            request: mmp.Profile,
            context: grpc.ServicerContext
            ) -> mmp.ProfileResult:
        """Forwards a submitted log message to the ProfilingStore."""
        # TODO: store
        return mmp.ProfileResult()

    def RequestSettings(
            self,
            request: mmp.SettingsRequest,
            context: grpc.ServicerContext
            ) -> mmp.SettingsResult:
        """Returns the central base settings."""
        settings = list()   # type: List[mmp.Setting]
        for name, value in self.__settings.items():
            if isinstance(value, str):
                setting = mmp.Setting(
                        name=str(name),
                        value_type=mmp.SETTING_VALUE_TYPE_STRING,
                        value_string=value)
            elif isinstance(value, bool):
                # a bool is an int in Python, so this needs to go before the
                # branch for int
                setting = mmp.Setting(
                        name=str(name),
                        value_type=mmp.SETTING_VALUE_TYPE_BOOL,
                        value_bool=value)
            elif isinstance(value, int):
                setting = mmp.Setting(
                        name=str(name),
                        value_type=mmp.SETTING_VALUE_TYPE_INT,
                        value_int=value)
            elif isinstance(value, float):
                setting = mmp.Setting(
                        name=str(name),
                        value_type=mmp.SETTING_VALUE_TYPE_FLOAT,
                        value_float=value)
            elif isinstance(value, list):
                if len(value) == 0 or isinstance(value[0], float):
                    value = cast(List[float], value)
                    mmp_values = mmp.ListOfDouble(values=value)
                    setting = mmp.Setting(
                            name=str(name),
                            value_type=mmp.SETTING_VALUE_TYPE_LIST_FLOAT,
                            value_list_float=mmp_values)
                elif isinstance(value[0], list):
                    value = cast(List[List[float]], value)
                    rows = list()
                    for row in value:
                        mmp_row = mmp.ListOfDouble(values=row)
                        rows.append(mmp_row)
                    mmp_rows = mmp.ListOfListOfDouble(values=rows)

                    LLF = mmp.SETTING_VALUE_TYPE_LIST_LIST_FLOAT
                    setting = mmp.Setting(
                            name=str(name),
                            value_type=LLF,
                            value_list_list_float=mmp_rows)
            settings.append(setting)

        return mmp.SettingsResult(setting_values=settings)

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
            self.__log(LogLevel.INFO, 'Registered instance {}'.format(
                        request.instance_name))
            return mmp.RegistrationResult(status=mmp.RESULT_STATUS_SUCCESS)
        except ValueError:
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

        self.__log(LogLevel.INFO, 'Sent peers to {}'.format(
                    request.instance_name))
        return mmp.PeerResult(
                status=mmp.RESULT_STATUS_SUCCESS,
                conduits=mmp_conduits,
                peer_dimensions=mmp_dimensions,
                peer_locations=instance_locations)

    def DeregisterInstance(self, request: mmp.DeregistrationRequest,
                           context: grpc.ServicerContext
                           ) -> mmp.DeregistrationResult:
        """Handles an instance deregistration request."""
        try:
            self.__instance_registry.remove(Reference(request.instance_name))
            self.__log(LogLevel.INFO, 'Deregistered instance {}'.format(
                    request.instance_name))
            return mmp.DeregistrationResult(status=mmp.RESULT_STATUS_SUCCESS)
        except ValueError:
            return mmp.DeregistrationResult(
                    status=mmp.RESULT_STATUS_ERROR,
                    error_message=('No instance with name {} was registered'
                                   ).format(request.instance_name))

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

                for peer_indices in generate_indices(peer_dims[len(dims):]):
                    yield base + peer_indices

    def __log(self, level: LogLevel, msg: str) -> None:
        """Logs a message to the log file.

        Args:
            level: The level to log at.
            msg: The message to log.
        """
        self.__logger.log_message('muscle3_manager', Timestamp(time.time()),
                                  level, msg)


class MMPServer():
    """The MUSCLE Manager Protocol server.

    This class accepts connections from the instances comprising \
    the multiscale model to be executed, and services them using an \
    MMPServicer.
    """
    def __init__(
            self,
            logger: Logger,
            settings: Settings,
            instance_registry: InstanceRegistry,
            topology_store: TopologyStore
            ) -> None:
        self._instance_registry = instance_registry
        self._servicer = MMPServicer(logger, settings, instance_registry,
                                     topology_store)
        self._server = grpc.server(futures.ThreadPoolExecutor())
        mmp_grpc.add_MuscleManagerServicer_to_server(  # type: ignore
                self._servicer, self._server)
        self._server.add_insecure_port('[::]:9000')
        self._server.start()

    def get_location(self) -> str:
        """Returns this server's network location.

        This is a string of the form <hostname>:<port>.
        """
        hostname = socket.getfqdn()
        return '{}:{}'.format(hostname, 9000)

    def wait(self) -> None:
        """Waits for the server to finish.

        The server will shut down after every instance has been
        registered and deregistered again.
        """
        self._instance_registry.wait()
        time.sleep(1)
        self._server.stop(5)

    def stop(self) -> None:
        """Stops the server.

        This makes the server stop serving requests, and shuts down its
        background threads.
        """
        self._server.stop(0)
