import sys
from typing import cast, Dict, List, Optional, Tuple, Type, Union

from ymmsl import Conduit, Identifier, Operator, Reference

from libmuscle.communicator import Communicator, MessageObject, _NoDefault
from libmuscle.configuration import Configuration, ParameterValue
from libmuscle.configuration_store import ConfigurationStore


class ComputeElement:
    """Represents a Compute Element instance in a MUSCLE3 simulation.

    This class provides a low-level send/receive API for the instance
    to use.
    """
    def __init__(self, instance: str,
                 ports: Optional[Dict[Operator, List[str]]]=None
                 ) -> None:
        """Create a ComputeElement.

        Args:
            name: The name of the instance represented by this object.
            ports: A list of port names for each operator of this
                compute element.
        """
        # Note that these are accessed by Muscle3, but otherwise private.
        self._name, self._index = self.__make_full_name(Reference(instance))
        """Name and index of this compute element."""

        self._ports = ports
        """Ports for this instance."""

        self._configuration_store = ConfigurationStore()
        """Configuration (parameters) for this instance."""

        self._communicator = Communicator(self._name, self._index)
        """Communicator for this instance."""

        if ports is not None:
            self._port_operators = dict()   # type: Dict[str, Operator]
            for op, port_names in ports.items():
                for port in port_names:
                    self._port_operators[port] = op

    def _connect(self, conduits: List[Conduit],
                 peer_dims: Dict[Reference, List[int]],
                 peer_locations: Dict[Reference, List[str]]) -> None:
        """Connect this compute element to the given peers / conduits.

        Args:
            conduits: A list of conduits attached to this compute
                element.
            peer_dims: For each peer, the dimensions of the instance
                set.
            peer_locations: A list of locations for each peer instance.
        """
        if self._ports is None:
            self._ports = dict()
            self._port_operators = dict()
            for conduit in conduits:
                if conduit.sending_compute_element() == self._name:
                    port_name = str(conduit.sending_port())
                    if Operator.O_F not in self._ports:
                        self._ports[Operator.O_F] = list()
                    self._ports[Operator.O_F].append(port_name)
                    self._port_operators[port_name] = Operator.O_F
                elif conduit.receiving_compute_element() == self._name:
                    port_name = str(conduit.receiving_port())
                    if Operator.F_INIT not in self._ports:
                        self._ports[Operator.F_INIT] = list()
                    self._ports[Operator.F_INIT].append(port_name)
                    self._port_operators[port_name] = Operator.F_INIT

        self._communicator.connect(conduits, peer_dims, peer_locations)

    def init_instance(self) -> None:
        """Initialise this instance.

        This method must be called once at the beginning of the reuse
        loop, i.e. before the F_INIT operator.
        """
        config, overlay = self._communicator.receive_message(
                'muscle_parameters_in', True)
        if not isinstance(config, Configuration):
            raise RuntimeError('"{}" received a message on'
                               ' muscle_parameters_in that is not a'
                               ' Configuration. It seems that your simulation'
                               ' is miswired or the sending instance is'
                               ' broken.'.format(self._instance_name()))

        for key, value in config.items():
            overlay[key] = value
        self._configuration_store.overlay = overlay

    def get_parameter_value(self, name: str,
                            typ: Optional[str] = None
                            ) -> ParameterValue:
        """Returns the value of a model parameter.

        Args:
            name: The name of the parameter, without any instance
                    prefix.
            typ: The expected type of the value. If the value does
                    not match this type, a TypeError will be raised.
                    If not specified, any of the supported types
                    will be accepted, and you'll have to figure out
                    what you got yourself.

        Raises:
            KeyError: If no value was set for this parameter.
            TypeError: If the type of the parameter's value was not
                    as expected.
        """
        return self._configuration_store.get_parameter(Reference(name), typ)

    def get_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports that this CE has.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        if self._ports is None:
            raise RuntimeError(('The set of ports was requested for Compute'
                                ' Element "{}", but it has no ports. No ports'
                                ' were specified when it was created, and it'
                                ' has not (yet) been registered.').format(
                                    self._instance_name()))
        return self._ports

    def send_message(self, port_name: str, timestamp: float,
                     next_timestamp: Optional[float],
                     message: Union[bytes, MessageObject],
                     slot: Union[int, List[int]]=[]) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        self.__check_port(port_name)
        self._communicator.send_message(
                port_name, timestamp, next_timestamp, message,
                self._configuration_store.overlay, slot)

    def send_message_with_parameters(
            self, port_name: str, timestamp: float,
            next_timestamp: Optional[float],
            message: Union[bytes, MessageObject],
            parameters: Configuration, slot: Union[int, List[int]]=[]) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        In a submodel, user :meth:`send_message` instead. This function
        is intended for use by special compute elements that are
        ensemble-aware and either generate overlay parameter sets or
        pass them on.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            parameters: A parameter overlay to inject.
            slot: The slot to send the message on, if any.
        """
        self.__check_port(port_name)
        overlay = self._configuration_store.overlay.copy()
        for key, value in parameters.items():
            overlay[key] = value
        self._communicator.send_message(port_name, timestamp, next_timestamp,
                                        message, overlay, slot)

    def receive_message(self, port_name: str, decode: bool,
                        slot: Union[int, List[int]]=[],
                        default: Optional[MessageObject]=_NoDefault
                        ) -> MessageObject:
        """Receive a message from the outside world.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it
        (i.e. decode does not apply). If you didn't specify a default
        value (e.g. because there is no reasonable default, you really
        need the outside input) and the port is not connected, you'll
        get a RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            decode: Whether to MsgPack-decode the message (True) or
                    return raw bytes() (False).
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message, decoded from MsgPack if decode is
            True, otherwise as a raw bytes object.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        self.__check_port(port_name)
        msg, config = self._communicator.receive_message(
                port_name, decode, slot, default)
        if (self._port_operators[port_name] == Operator.F_INIT and
                len(self._configuration_store.overlay) == 0):
            self._configuration_store.overlay = config
        else:
            if self._configuration_store.overlay != config:
                raise RuntimeError(('Unexpectedly received data from a'
                                    ' parallel universe on port "{}". My'
                                    ' parameters are "{}" and I received from'
                                    ' a universe with "{}".').format(
                                        port_name,
                                        self._configuration_store.overlay,
                                        config))
        return msg

    def receive_message_with_parameters(
            self, port_name: str, decode: bool, slot: Union[int, List[int]]=[],
            default: Optional[MessageObject]=_NoDefault
            ) -> Tuple[MessageObject, Configuration]:
        """Receive a message with attached parameter overlay.

        This function should not be used in submodels. It is intended
        for use by special compute elements that are ensemble-aware and
        have to pass on overlay parameter sets explicitly.

        Receiving is a blocking operaton. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        If the port you are receiving on is not connected, the default
        value you specified will be returned exactly as you passed it
        (i.e. decode does not apply), together with an empty
        Configuration. If you didn't specify a default value (e.g.
        because there is no reasonable default, and you really need the
        outside input) and the port is not connected, then you'll get a
        RuntimeError.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            decode: Whether to MsgPack-decode the message (True) or
                    return raw bytes() (False).
            slot: The slot to receive the message on, if any.
            default: A default value to return if this port is not
                    connected.

        Returns:
            The received message, decoded from MsgPack if decode is
            True and otherwise as a raw bytes object, and a
            Configuration holding the parameter overlay.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        self.__check_port(port_name)
        return self._communicator.receive_message(port_name, decode, slot,
                                                  default)

    def __make_full_name(self, instance: Reference
                         ) -> Tuple[Reference, List[int]]:
        """Returns instance name and index.

        The given instance string is split into a compute element and
        an index, which are returned.

        If a --muscle-index=x,y,z is given on the command line, then
        it is parsed and prepended on the index. If there is no
        --muscle-index on the command line, and instance does not
        contain an index either, then this returns an empty list for
        the second item.
        """
        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        index = list()     # type: List[int]
        prefix = '--muscle-index='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                index_str = arg[len(prefix):]
                indices = index_str.split(',')
                index += map(int, indices)
                break

        i = 0
        while i < len(instance) and isinstance(instance[i], Identifier):
            i += 1
        kernel = instance[:i]

        while i < len(instance) and isinstance(instance[i], int):
            index.append(cast(int, instance[i]))
            i += 1

        return kernel, index

    def _instance_name(self) -> Reference:
        """Returns the full instance name.
        """
        return self._name + self._index

    def __check_port(self, port_name: str) -> None:
        ports = cast(Dict[Operator, List[str]], self._ports)
        for operator, port_names in ports.items():
            for registered_port in port_names:
                if port_name == registered_port:
                    return
        raise ValueError(('Port "{}" does not exist on "{}". Please check the'
                          ' name and the list of ports you gave for this'
                          ' compute element.').format(port_name, self._name))
