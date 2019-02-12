import sys
from typing import Dict, List, Optional, Type, Union

from ymmsl import Operator, Reference

from libmuscle.communicator import Communicator, Message
from libmuscle.configuration import ParameterValue
from libmuscle.configuration_store import ConfigurationStore


class ComputeElement:
    """Represents a Compute Element instance in a MUSCLE3 simulation.

    This class provides a low-level send/receive API for the instance
    to use.
    """
    def __init__(self, instance: str, ports: Dict[Operator, List[str]]
                 ) -> None:
        """Create a ComputeElement.

        Args:
            instance: The name of the instance represented by this
                class.
            ports: A list of port names for each operator of this
                compute element.
        """
        # Note that these are accessed by Muscle3, but otherwise private.
        self._name = self.__make_full_name(instance)
        """Name of this instance."""

        self._ports = ports
        """Ports for this instance."""

        self._configuration_store = ConfigurationStore()
        """Configuration (parameters) for this instance."""

        port_operators = dict()
        for op, port_names in ports.items():
            for port in port_names:
                port_operators[port] = op

        self._communicator = Communicator(
                self._name, self._configuration_store, port_operators)
        """Communicator for this instance."""

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

    def send_message(self, port_name: str, message: Union[bytes, Message],
                     slot: Union[int, List[int]]=[]) -> None:
        """Send a message to the outside world.

        Sending is non-blocking, a copy of the message will be made
        and stored until the receiver is ready to receive it.

        Args:
            port_name: The port on which this message is to be sent.
            message: The message to be sent.
            slot: The slot to send the message on, if any.
        """
        self._communicator.send_message(port_name, message, slot=slot)

    def receive_message(self, port_name: str, decode: bool,
                        slot: Union[int, List[int]]=[]) -> Message:
        """Receive a message from the outside world.

        Receiving is a blocking operation. This function will contact
        the sender, wait for a message to be available, and receive and
        return it.

        Args:
            port_name: The endpoint on which a message is to be
                    received.
            decode: Whether to MsgPack-decode the message (True) or
                    return raw bytes() (False).
            slot: The slot to receive the message on, if any.

        Returns:
            The received message, decoded from MsgPack if decode is
            True, otherwise as a raw bytes object.
        """
        return self._communicator.receive_message(port_name, decode, slot)

    def __make_full_name(self, name: str) -> Reference:
        """Makes a Reference of the name and optionally index.

        If a --muscle-index=x,y,z is given on the command line, then
        it is appended to the name.
        """
        full_name = Reference(name)

        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix = '--muscle-index='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                index_str = arg[len(prefix):]
                indices = index_str.split(',')
                full_name += map(int, indices)
                break

        return full_name
