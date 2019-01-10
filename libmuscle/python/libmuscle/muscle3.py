import sys
from typing import Dict, List, Optional

from ymmsl import Identifier, Operator, Port, Reference

from libmuscle.compute_element import ComputeElement
from libmuscle.mmp_client import MMPClient


class Muscle3:
    """The main MUSCLE 3 API class.

    This class provides the main MUSCLE3 functionality needed to
    implement compute elements that work in MUSCLE.
    """
    def __init__(self) -> None:
        """Initialise MUSCLE3.

        Creating an object of type Muscle initialises MUSCLE3 and
        makes its functionality available.
        """
        self.__manager = None  # type: Optional[MMPClient]
        mmp_location = self.__extract_manager_location()
        if mmp_location is not None:
            self.__manager = MMPClient(mmp_location)

    def register(self, name: str, ports: Dict[Operator, List[str]],
                 element: ComputeElement) -> None:
        """Register a compute element with MUSCLE3.

        Args:
            name: The name of this element or instance.
            ports: A dictionary mapping operators to a list of port
                names for that operator.
            element: The compute element to register.
        """
        full_name = self.__make_full_name(name)
        locations = element._communicator.get_locations()
        port_list = self.__port_list_from_ports(ports)
        if self.__manager is not None:
            self.__manager.register_instance(full_name, locations, port_list)
            conduits, peer_dims, peer_locations = self.__manager.request_peers(
                    full_name)
            element._communicator.connect(conduits, peer_dims, peer_locations)

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

    def __port_list_from_ports(self, ports: Dict[Operator, List[str]]
                               ) -> List[Port]:
        """Converts a dict of ports per operator to a list of ports.

        Args:
            ports: The ports as passed by the user.

        Returns:
            The ports as expected by MMP.
        """
        result = list()
        for operator, port_names in ports.items():
            for name in port_names:
                result.append(Port(Identifier(name), operator))
        return result

    @staticmethod
    def __extract_manager_location() -> Optional[str]:
        """Gets the manager network location from the command line.

        We use a --muscle-manager=<host:port> argument to tell the
        MUSCLE library how to connect to the manager. This function
        will extract this argument from the command line arguments,
        if it is present. Since we want to be able to run without
        a manager, it is optional.

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

        return None
