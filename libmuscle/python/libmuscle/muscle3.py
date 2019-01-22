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

    def register(self, elements: List[ComputeElement]) -> None:
        """Register a compute element with MUSCLE3.

        Args:
            elements: The compute elements to register.
        """
        if self.__manager is not None:
            for element in elements:
                locations = element._communicator.get_locations()
                port_list = self.__port_list_from_ports(element._ports)
                self.__manager.register_instance(element._name, locations,
                                                 port_list)

            configuration = self.__manager.get_configuration()

            for element in elements:
                conduits, dims, locs = self.__manager.request_peers(
                        element._name)
                element._communicator.connect(conduits, dims, locs)
                element._configuration_store._base = configuration

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
