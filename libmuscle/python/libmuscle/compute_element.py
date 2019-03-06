from copy import copy
import sys
from typing import cast, Dict, List, Optional, Tuple, Type, Union

from ymmsl import Conduit, Identifier, Operator, Reference

from libmuscle.communicator import _ClosePort, Communicator, Message
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

        self._communicator = Communicator(self._name, self._index, ports)
        """Communicator for this instance."""

        self._declared_ports = ports
        """Declared ports for this instance."""

        self._configuration_store = ConfigurationStore()
        """Configuration (parameters) for this instance."""

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
        self._communicator.connect(conduits, peer_dims, peer_locations)

    def reuse_instance(self) -> None:
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
        shut down. Whether to do another F_INIT, O_I, S, B, O_F cycle
        is decided by this method.

        This method must be called at the beginning of the reuse loop,
        i.e. before the F_INIT operator, and its return value should
        decide whether to enter that loop again.
        """
        message = self._communicator.receive_message(
                'muscle_parameters_in')
        if not isinstance(message.data, Configuration):
            raise RuntimeError('"{}" received a message on'
                               ' muscle_parameters_in that is not a'
                               ' Configuration. It seems that your simulation'
                               ' is miswired or the sending instance is'
                               ' broken.'.format(self._instance_name()))

        configuration = cast(Configuration, message.configuration)
        for key, value in message.data.items():
            configuration[key] = value
        self._configuration_store.overlay = configuration

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

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports that this CE has.

        This method will return an empty dictionary if _connect() has
        not yet been called.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        return self._communicator.list_ports()

    def is_vector_port(self, port: str) -> bool:
        """Returns whether a port is a vector or scalar port

        If a port has been declared to be a vector port (i.e. the
        name passed when creating this ComputeElement had '[]' at the
        end), then you can pass a 'slot' argument when sending or
        receiving. It's like the port is a vector of slots on which
        you can send or receive messages.

        This function returns True if the given port is a vector
        port, and False if it is a scalar port.

        Args:
            port: The port to check this property of.
        """
        return self._communicator.get_port(port).is_vector()

    def send_message(self, port_name: str, message: Message,
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
        if message.configuration is None:
            message = copy(message)
            message.configuration = self._configuration_store.overlay

        self._communicator.send_message(port_name, message, slot)

    def receive_message(self, port_name: str, slot: Union[int, List[int]]=[],
                        default: Optional[Message]=None
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
            The received message.The configuration attribute of the
            received message will be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        self.__check_port(port_name)
        msg = self._communicator.receive_message(
                port_name, slot, default)
        operator = self._communicator.get_port(port_name).operator
        if (operator == Operator.F_INIT and
                len(self._configuration_store.overlay) == 0):
            self._configuration_store.overlay = cast(
                    Configuration, msg.configuration)
        else:
            if self._configuration_store.overlay != msg.configuration:
                raise RuntimeError(('Unexpectedly received data from a'
                                    ' parallel universe on port "{}". My'
                                    ' parameters are "{}" and I received from'
                                    ' a universe with "{}".').format(
                                        port_name,
                                        self._configuration_store.overlay,
                                        msg.configuration))
        msg.configuration = None
        return msg

    def receive_message_with_parameters(
            self, port_name: str, slot: Union[int, List[int]]=[],
            default: Optional[Message]=None
            ) -> Message:
        """Receive a message with attached parameter overlay.

        This function should not be used in submodels. It is intended
        for use by special compute elements that are ensemble-aware and
        have to pass on overlay parameter sets explicitly.

        Receiving is a blocking operaton. This function will contact
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
            The received message. The configuration attribute will
            contain the received Configuration, and will not be None.

        Raises:
            RuntimeError: If the given port is not connected and no
                    default value was given.
        """
        self.__check_port(port_name)
        return self._communicator.receive_message(port_name, slot, default)

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
        if not self._communicator.port_exists(port_name):
            raise ValueError(('Port "{}" does not exist on "{}". Please check'
                              ' the name and the list of ports you gave for'
                              ' this compute element.').format(port_name,
                                                               self._name))
