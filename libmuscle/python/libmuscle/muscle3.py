import multiprocessing as mp
import sys
from typing import cast, Callable, Dict, List, Optional, Union

from ymmsl import Identifier, Operator, Port, Reference

from libmuscle.compute_element import ComputeElement
from libmuscle.mcp import pipe_multiplexer as mux
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

    def register(self, elements: Union[ComputeElement, List[ComputeElement]]
                 ) -> None:
        """Register a compute element with MUSCLE3.

        Args:
            elements: The compute elements to register.
        """
        if isinstance(elements, ComputeElement):
            elements = [elements]
        self.__instances = list()   # type: List[Reference]
        if self.__manager is not None:
            for element in elements:
                locations = element._communicator.get_locations()
                port_list = self.__port_list_from_ports(
                        element._declared_ports)
                instance_name = element._name + element._index
                self.__manager.register_instance(instance_name, locations,
                                                 port_list)
                self.__instances.append(instance_name)

            configuration = self.__manager.get_configuration()

            for element in elements:
                instance_name = element._name + element._index
                conduits, dims, locs = self.__manager.request_peers(
                        element._instance_name())
                element._connect(conduits, dims, locs)
                element._configuration_store.base = configuration

    def close(self) -> None:
        """Deregister all registered instances.
        """
        if self.__manager is not None:
            for instance in self.__instances:
                self.__manager.deregister_instance(instance)

    def __port_list_from_ports(self, ports: Optional[Dict[Operator, List[str]]]
                               ) -> List[Port]:
        """Converts a dict of ports per operator to a list of ports.

        Args:
            ports: The ports as passed by the user.

        Returns:
            The ports as expected by MMP.
        """
        result = list()
        if ports is not None:
            for operator, port_names in ports.items():
                for name in port_names:
                    if name.endswith('[]'):
                        name = name[:-2]
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


def run_instances(instances: Dict[str, Callable]) -> None:
    """Runs the given instances and waits for them to finish.

    The instances are described in a dictionary with their instance
    id (e.g. 'macro' or 'micro[12]' or 'my_mapper') as the key, and
    a function to run as the corresponding value. Each instance
    will be run in a separate process.

    Args:
        instances: A dictionary of instances to run.
    """
    instance_processes = list()
    for instance_id_str, implementation in instances.items():
        mux.add_instance(Reference(instance_id_str))

    for instance_id_str, implementation in instances.items():
        instance_id = Reference(instance_id_str)
        process = mp.Process(target=implementation,
                             args=(instance_id_str,),
                             name='Instance-{}'.format(instance_id))
        process.start()
        mux.close_instance_ends(instance_id)
        instance_processes.append(process)

    mux_process = mp.Process(target=mux.run, name='PipeCommMultiplexer')
    mux_process.start()
    mux.close_all_pipes()

    for instance_process in instance_processes:
        instance_process.join()
    mux_process.join()
