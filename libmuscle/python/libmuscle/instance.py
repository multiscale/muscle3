from copy import copy
import logging
import os
from pathlib import Path
import sys
from typing import cast, Dict, List, Optional, Tuple

import grpc
from ymmsl import (Identifier, Operator, SettingValue, Port, Reference,
                   Settings)

from libmuscle.communicator import Communicator, Message
from libmuscle.settings_manager import SettingsManager
from libmuscle.logging_handler import MuscleManagerHandler
from libmuscle.mcp.message import ClosePort
from libmuscle.mmp_client import MMPClient
from libmuscle.profiler import Profiler
from libmuscle.profiling import ProfileEventType
from libmuscle.util import extract_log_file_location


_logger = logging.getLogger(__name__)


_FInitCacheType = Dict[Tuple[str, Optional[int]], Message]


class Instance:
    """Represents a compute element instance in a MUSCLE3 simulation.

    This class provides a low-level send/receive API for the instance
    to use.
    """
    def __init__(self, ports: Optional[Dict[Operator, List[str]]] = None
                 ) -> None:
        """Create an Instance.

        Args:
            ports: A list of port names for each operator of this
                compute element.
        """
        self.__is_shut_down = False

        # Note that these are accessed by Muscle3, but otherwise private.
        self._name, self._index = self.__make_full_name()
        """Name and index of this instance."""

        mmp_location = self.__extract_manager_location()
        self.__manager = MMPClient(mmp_location)
        """Client object for talking to the manager."""

        self.__set_up_logging()

        self._profiler = Profiler(self._instance_name(), self.__manager)
        """Profiler for this instance."""

        self._communicator = Communicator(
                self._name, self._index, ports, self._profiler)
        """Communicator for this instance."""

        self._declared_ports = ports
        """Declared ports for this instance."""

        self._settings_manager = SettingsManager()
        """Settings for this instance."""

        self._first_run = True
        """Keeps track of whether this is the first reuse run."""

        self._f_init_cache = dict()     # type: _FInitCacheType

        self._register()
        self._connect()
        self._set_log_level()

    def reuse_instance(self, apply_overlay: bool = True) -> bool:
        """Decide whether to run this instance again.

        In a multiscale simulation, instances get reused all the time.
        For example, in a macro-micro simulation, the micromodel does a
        complete run for every timestep of the macromodel. Rather than
        starting up a new instance of the micromodel, which could be
        expensive, we reuse a single instance many times.

        This may bring other advantages, such as faster convergence
        when starting from the previous final state, and in some
        cases may be necessary if micromodel state needs to be
        preserved from one macro timestep to the next.

        So in MUSCLE, submodels run in a *reuse loop*, which runs them
        over and over again until their work is done and they should be
        shut down. Whether to do another F_INIT, O_I, S, O_F cycle
        is decided by this method.

        This method must be called at the beginning of the reuse loop,
        i.e. before the F_INIT operator, and its return value should
        decide whether to enter that loop again.

        Args:
            apply_overlay: Whether to apply the received settings
                overlay or to save it. If you're going to use
                :meth:`receive_with_settings` on your F_INIT ports,
                set this to False. If you don't know what that means,
                just call `reuse_instance()` without specifying this
                and everything will be fine. If it turns out that you
                did need to specify False, MUSCLE 3 will tell you about
                it in an error message and you can add it still.
        """
        do_reuse = self.__receive_settings()

        # TODO: _f_init_cache should be empty here, or the user didn't
        # receive something that was sent on the last go-around.
        # At least emit a warning.
        self.__pre_receive_f_init(apply_overlay)

        self._set_log_level()

        ports = self._communicator.list_ports()
        f_init_not_connected = all(
                [not self.is_connected(port)
                 for port in ports.get(Operator.F_INIT, [])])
        no_settings_in = not self._communicator.settings_in_connected()

        if f_init_not_connected and no_settings_in:
            do_reuse = self._first_run
            self._first_run = False
        else:
            for message in self._f_init_cache.values():
                if isinstance(message.data, ClosePort):
                    do_reuse = False

        if not do_reuse:
            self.__close_ports()
            self._communicator.shutdown()
            self._deregister()
        return do_reuse

    def error_shutdown(self, message: str) -> None:
        """Logs an error and shuts down the Instance.

        If you detect that something is wrong (invalid input, invalid
        settings, simulation diverged, or anything else really), you
        should call this method before calling exit() or raising
        an exception that you don't expect to catch.

        If you do so, the Instance will tell the rest of the simulation
        that it encountered an error and will shut down. That makes it
        easier to debug the situation (the message will be logged), and
        it reduces the chance that other parts of the simulation will
        sit around waiting forever for a message that this instance was
        supposed to send.

        Args:
            message: An error message describing the problem.
        """
        self.__shutdown(message)

    def get_setting(self, name: str, typ: Optional[str] = None
                    ) -> SettingValue:
        """Returns the value of a model setting.

        Args:
            name: The name of the setting, without any instance
                    prefix.
            typ: The expected type of the value. If the value does
                    not match this type, a TypeError will be raised.
                    If not specified, any of the supported types
                    will be accepted, and you'll have to figure out
                    what you got yourself.

        Raises:
            KeyError: If no value was set for this setting.
            TypeError: If the type of the setting's value was not
                    as expected.
        """
        return self._settings_manager.get_setting(
                self._instance_name(), Reference(name), typ)

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports that this CE has.

        Note that the result has almost the same format as the port
        declarations you pass when making an Instance. The only
        difference is that the port names never have `[]` at the end,
        even if the port is a vector port.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        return self._communicator.list_ports()

    def is_connected(self, port: str) -> bool:
        """Returns whether the given port is connected.

        Args:
            port: The name of the port to inspect.

        Returns:
            True if there is a conduit attached to this port, False
            if not.
        """
        return self._communicator.get_port(port).is_connected()

    def is_vector_port(self, port: str) -> bool:
        """Returns whether a port is a vector or scalar port

        If a port has been declared to be a vector port (i.e. the
        name passed when creating this Instance had '[]' at the
        end), then you can pass a 'slot' argument when sending or
        receiving. It's like the port is a vector of slots on which
        you can send or receive messages.

        This function returns True if the given port is a vector
        port, and False if it is a scalar port.

        Args:
            port: The port to check this property of.
        """
        return self._communicator.get_port(port).is_vector()

    def is_resizable(self, port: str) -> bool:
        """Returns whether the given port is resizable.

        Scalar ports are never resizable. Whether a vector port is
        resizable depends on what it is connected to.

        Args:
            port: Name of the port to inspect.

        Returns:
            True if the port can be resized.
        """
        return self._communicator.get_port(port).is_resizable()

    def get_port_length(self, port: str) -> int:
        """Returns the current length of the port.

        Args:
            port: The name of the port to measure.

        Raises: RuntimeError if this is a scalar port.
        """
        return self._communicator.get_port(port).get_length()

    def set_port_length(self, port: str, length: int) -> None:
        """Resizes the port to the given length.

        You should check whether the port is resizable using
        `is_resizable()` first; whether it is depends on how this
        compute element is wired up, so you should check.

        Args:
            port: Name of the port to resize.
            length: The new length.

        Raises:
            RuntimeError: If the port is not resizable.
        """
        self._communicator.get_port(port).set_length(length)

    def send(self, port_name: str, message: Message,
             slot: Optional[int] = None) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        self.__check_port(port_name)
        if message.settings is None:
            message = copy(message)
            message.settings = self._settings_manager.overlay

        self._communicator.send_message(port_name, message, slot)

    def receive(self, port_name: str, slot: Optional[int] = None,
                default: Optional[Message] = None
                ) -> Message:
        """Receive a message from the outside world.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it.
        If you didn't specify a default value (e.g. because there is no
        reasonable default, you really need the outside input) and the
        port is not connected, you'll get a RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message. The settings attribute of the
            received message will be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        return self.__receive_message(port_name, slot, default, False)

    def receive_with_settings(
            self, port_name: str, slot: Optional[int] = None,
            default: Optional[Message] = None
            ) -> Message:
        """Receive a message with attached settings overlay.

        This function should not be used in submodels. It is intended
        for use by special compute elements that are ensemble-aware and
        have to pass on overlay settings explicitly.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it.
        If you didn't specify a default value (e.g. because there is no
        reasonable default, and you really need the outside input) and
        the port is not connected, then you'll get a RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message. The settings attribute will
            contain the received Settings, and will not be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        return self.__receive_message(port_name, slot, default, True)

    def _register(self) -> None:
        """Register this instance with the manager.
        """
        register_event = self._profiler.start(ProfileEventType.REGISTER)
        locations = self._communicator.get_locations()
        port_list = self.__list_declared_ports()
        self.__manager.register_instance(self._instance_name(), locations,
                                         port_list)
        try:
            register_event.stop()
        except grpc._channel._Rendezvous:
            # This may happen if we're the last submodel to quit, and the
            # manager is already gone. Nothing we can do in that case, and this
            # final Register event will be lost, which is not a big issue.
            pass

    def _connect(self) -> None:
        """Connect this instance to the given peers / conduits.
        """
        connect_event = self._profiler.start(ProfileEventType.CONNECT)
        conduits, peer_dims, peer_locations = self.__manager.request_peers(
                self._instance_name())
        self._communicator.connect(conduits, peer_dims, peer_locations)
        self._settings_manager.base = self.__manager.get_settings()
        connect_event.stop()

    def _deregister(self) -> None:
        """Deregister this instance from the manager.
        """
        deregister_event = self._profiler.start(ProfileEventType.DEREGISTER)
        self.__manager.deregister_instance(self._instance_name())
        deregister_event.stop()
        # this is the last thing we'll profile, so flush messages
        self._profiler.shutdown()

    @staticmethod
    def __extract_manager_location() -> str:
        """Gets the manager network location from the command line.

        We use a --muscle-manager=<host:port> argument to tell the
        MUSCLE library how to connect to the manager. This function
        will extract this argument from the command line arguments,
        if it is present.

        Returns:
            A connection string, or None.
        """
        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix = '--muscle-manager='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                return arg[len(prefix):]

        return 'localhost:9000'

    def __set_up_logging(self) -> None:
        """Adds logging handlers for one or more instances.
        """
        id_str = str(self._instance_name())

        logfile = extract_log_file_location(
                Path.cwd(), 'muscle3.{}.log'.format(id_str))
        local_handler = logging.FileHandler(str(logfile), mode='w')
        formatter = logging.Formatter('%(asctime)-15s: %(name)s'
                                      ' %(levelname)s: %(message)s')
        local_handler.setFormatter(formatter)
        logging.getLogger().addHandler(local_handler)

        if self.__manager is not None:
            self._mmp_handler = MuscleManagerHandler(id_str, logging.WARNING,
                                                     self.__manager)
            logging.getLogger().addHandler(self._mmp_handler)

    def __receive_message(
            self, port_name: str, slot: Optional[int],
            default: Optional[Message], with_settings: bool
            ) -> Message:
        """Receives a message on the given port.

        This implements receive and receive_with_settings, see the
        description of those.
        """
        self.__check_port(port_name)

        port = self._communicator.get_port(port_name)
        if port.operator == Operator.F_INIT:
            if (port_name, slot) in self._f_init_cache:
                msg = self._f_init_cache[(port_name, slot)]
                del(self._f_init_cache[(port_name, slot)])
                if with_settings and msg.settings is None:
                    err_msg = ('If you use receive_with_settings()'
                               ' on an F_INIT port, then you have to'
                               ' pass False to reuse_instance(),'
                               ' otherwise the settings will already'
                               ' have been applied by MUSCLE.')
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)
            else:
                if port.is_connected():
                    err_msg = (('Tried to receive twice on the same'
                                ' port "{}", that\'s not possible.'
                                ' Did you forget to call'
                                ' reuse_instance() in your reuse loop?'
                                ).format(port_name))
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)
                else:
                    if default is not None:
                        return default
                    err_msg = (('Tried to receive on port "{}",'
                                ' which is not connected, and no'
                                ' default value was given. Please'
                                ' connect this port!').format(port_name))
                    self.__shutdown(err_msg)
                    raise RuntimeError(err_msg)

        else:
            msg = self._communicator.receive_message(
                    port_name, slot, default)
            if port.is_connected and not port.is_open(slot):
                err_msg = (('Port {} was closed while trying to'
                            ' receive on it, did the peer crash?'
                            ).format(port_name))
                self.__shutdown(err_msg)
                raise RuntimeError(err_msg)
            if port.is_connected and not with_settings:
                self.__check_compatibility(port_name, msg.settings)
            if not with_settings:
                msg.settings = None
        return msg

    def __make_full_name(self
                         ) -> Tuple[Reference, List[int]]:
        """Returns instance name and index.

        This takes the argument to the --muscle-instance= command-line
        option and splits it into a compute element name and an index.
        """
        def split_reference(ref: Reference) -> Tuple[Reference, List[int]]:
            index = list()     # type: List[int]
            i = 0
            while i < len(ref) and isinstance(ref[i], Identifier):
                i += 1
            name = cast(Reference, ref[:i])

            while i < len(ref) and isinstance(ref[i], int):
                index.append(cast(int, ref[i]))
                i += 1

            return name, index

        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix_tag = '--muscle-instance='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix_tag):
                prefix_str = arg[len(prefix_tag):]
                prefix_ref = Reference(prefix_str)
                name, index = split_reference(prefix_ref)
                break
        else:
            if 'MUSCLE_INSTANCE' in os.environ:
                prefix_ref = Reference(os.environ['MUSCLE_INSTANCE'])
                name, index = split_reference(prefix_ref)
            else:
                raise RuntimeError((
                    'A --muscle-instance command line argument or'
                    ' MUSCLE_INSTANCE environment variable is required to'
                    ' identify this instance. Please add one.'))
        return name, index

    def __list_declared_ports(self) -> List[Port]:
        """Returns a list of declared ports.

        This returns a list of ymmsl.Port objects, which have only the
        name and the operator, not libmuscle.Port, which has more.
        """
        result = list()
        if self._declared_ports is not None:
            for operator, port_names in self._declared_ports.items():
                for name in port_names:
                    if name.endswith('[]'):
                        name = name[:-2]
                    result.append(Port(Identifier(name), operator))
        return result

    def _instance_name(self) -> Reference:
        """Returns the full instance name.
        """
        return self._name + self._index

    def __check_port(self, port_name: str) -> None:
        if not self._communicator.port_exists(port_name):
            err_msg = (('Port "{}" does not exist on "{}". Please check'
                        ' the name and the list of ports you gave for'
                        ' this compute element.').format(port_name,
                                                         self._name))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

    def __receive_settings(self) -> bool:
        """Receives settings on muscle_settings_in.

        Returns:
            False iff the port is connnected and ClosePort was received.
        """
        default_message = Message(0.0, None, Settings(), Settings())
        message = self._communicator.receive_message(
                'muscle_settings_in', None, default_message)
        if isinstance(message.data, ClosePort):
            return False
        if not isinstance(message.data, Settings):
            err_msg = ('"{}" received a message on'
                       ' muscle_settings_in that is not a'
                       ' Settings. It seems that your'
                       ' simulation is miswired or the sending'
                       ' instance is broken.'.format(self._instance_name()))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

        settings = cast(Settings, message.settings)
        for key, value in message.data.items():
            settings[key] = value
        self._settings_manager.overlay = settings
        return True

    def __pre_receive_f_init(self, apply_overlay: bool) -> None:
        """Receives on all ports connected to F_INIT.

        This receives all incoming messages on F_INIT and stores them
        in self._f_init_cache.
        """
        def pre_receive(port_name: str, slot: Optional[int]) -> None:
            msg = self._communicator.receive_message(port_name, slot)
            self._f_init_cache[(port_name, slot)] = msg
            if apply_overlay:
                self.__apply_overlay(msg)
                self.__check_compatibility(port_name, msg.settings)
                msg.settings = None

        self._f_init_cache = dict()
        ports = self._communicator.list_ports()
        for port_name in ports.get(Operator.F_INIT, []):
            _logger.info('Pre-receiving on port {}'.format(port_name))
            port = self._communicator.get_port(port_name)
            if not port.is_connected():
                continue
            if not port.is_vector():
                pre_receive(port_name, None)
            else:
                pre_receive(port_name, 0)
                # The above receives the length, if needed, so now we can
                # get the rest.
                for slot in range(1, port.get_length()):
                    pre_receive(port_name, slot)

    def _set_log_level(self) -> None:
        """Sets the remote log level.

        This is the minimum level a message must have to be sent to
        the manager. It gets this from the muscle_remote_log_level
        setting.

        Note that this also sets the global log level to this level
        if it is currently higher, otherwise we still get no output.

        """
        try:
            log_level_str = cast(
                    str, self.get_setting('muscle_remote_log_level', 'str'))
            level_map = {
                    'CRITICAL': logging.CRITICAL,
                    'ERROR': logging.ERROR,
                    'WARNING': logging.WARNING,
                    'INFO': logging.INFO,
                    'DEBUG': logging.DEBUG}

            if log_level_str.upper() not in level_map:
                _logger.warning(
                    ('muscle_remote_log_level is set to {}, which is not a'
                     ' valid log level. Please use one of DEBUG, INFO,'
                     ' WARNING, ERROR, or CRITICAL').format(log_level_str))
                return

            log_level = level_map[log_level_str]
            self._mmp_handler.setLevel(log_level)
            if not logging.getLogger().isEnabledFor(log_level):
                logging.getLogger().setLevel(log_level)
        except KeyError:
            # muscle_remote_log_level not set, do nothing and keep the default
            pass

    def __apply_overlay(self, message: Message) -> None:
        """Sets local overlay if we don't already have one.

        Args:
            message: The message to apply the overlay from.
        """
        if len(self._settings_manager.overlay) == 0:
            if message.settings is not None:
                self._settings_manager.overlay = message.settings

    def __check_compatibility(self, port_name: str,
                              overlay: Optional[Settings]) -> None:
        """Checks whether a received overlay matches the current one.

        Args:
            port_name: Name of the port on which the overlay was
                    received.
            overlay: The received overlay.
        """
        if overlay is None:
            return
        if self._settings_manager.overlay != overlay:
            err_msg = (('Unexpectedly received data from a'
                        ' parallel universe on port "{}". My'
                        ' settings are "{}" and I received'
                        ' from a universe with "{}".').format(
                            port_name, self._settings_manager.overlay,
                            overlay))
            self.__shutdown(err_msg)
            raise RuntimeError(err_msg)

    def __close_outgoing_ports(self) -> None:
        """Closes outgoing ports.

        This sends a close port message on all slots of all outgoing
        ports.
        """
        for operator, ports in self._communicator.list_ports().items():
            if operator.allows_sending():
                for port_name in ports:
                    port = self._communicator.get_port(port_name)
                    if port.is_vector():
                        for slot in range(port.get_length()):
                            self._communicator.close_port(port_name, slot)
                    else:
                        self._communicator.close_port(port_name)

    def __drain_incoming_port(self, port_name: str) -> None:
        """Receives messages until a ClosePort is received.

        Receives at least once.

        Args:
            port_name: Port to drain.
        """
        port = self._communicator.get_port(port_name)
        while port.is_open():
            # TODO: log warning if not a ClosePort
            self._communicator.receive_message(port_name)

    def __drain_incoming_vector_port(self, port_name: str) -> None:
        """Receives messages until a ClosePort is received.

        Works with (resizable) vector ports.

        Args:
            port_name: Port to drain.
        """
        port = self._communicator.get_port(port_name)
        while not all([not port.is_open(slot)
                       for slot in range(port.get_length())]):
            for slot in range(port.get_length()):
                if port.is_open(slot):
                    self._communicator.receive_message(port_name, slot)

    def __close_incoming_ports(self) -> None:
        """Closes incoming ports.

        This receives on all incoming ports until a ClosePort is
        received on them, signaling that there will be no more
        messages, and allowing the sending instance to shut down
        cleanly.
        """
        for operator, port_names in self._communicator.list_ports().items():
            if operator.allows_receiving():
                for port_name in port_names:
                    port = self._communicator.get_port(port_name)
                    if not port.is_connected():
                        continue
                    if not port.is_vector():
                        self.__drain_incoming_port(port_name)
                    else:
                        self.__drain_incoming_vector_port(port_name)

    def __close_ports(self) -> None:
        """Closes all ports.

        This sends a close port message on all slots of all outgoing
        ports, then receives one on all incoming ports.
        """
        self.__close_outgoing_ports()
        self.__close_incoming_ports()

    def __shutdown(self, message: str) -> None:
        """Shuts down simulation.

        This logs the given error message, communicates to the peers
        that we're shutting down, and deregisters from the manager.
        """
        if not self.__is_shut_down:
            _logger.critical(message)
            self.__close_ports()
            self._communicator.shutdown()
            self._deregister()
            self.__is_shut_down = True
