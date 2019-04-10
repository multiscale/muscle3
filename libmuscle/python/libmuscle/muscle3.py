import copy
import logging
import multiprocessing as mp
from pathlib import Path
import sys
from typing import cast, Callable, Dict, List, Optional, Union

from ymmsl import Identifier, Operator, Port, Reference

from libmuscle.compute_element import ComputeElement
from libmuscle.logging_handler import MuscleManagerHandler
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
        mmp_location = self.__extract_manager_location()
        self.__manager = MMPClient(mmp_location)

    def compute_element(self, instance_id: str,
                        ports: Optional[Dict[Operator, List[str]]]=None
                        ) -> ComputeElement:
        """Creates a new ComputeElement object.

        Args:
            instance_id: Id of this instance, e.g. "macro" or
                    "micro[3]".
            ports: The ports that this ComputeElement has, as a list
                    of port descripions per operator.

        Returns:
            A new ComputeElement with the given id and ports.
        """
        return ComputeElement(self.__manager, instance_id, ports)

    def register(self, elements: Union[ComputeElement, List[ComputeElement]]
                 ) -> None:
        """Register a compute element with MUSCLE3.

        Args:
            elements: The compute elements to register.
        """
        if isinstance(elements, ComputeElement):
            elements = [elements]

        self.__set_up_logging(elements)

        self.__instances = list()   # type: List[ComputeElement]
        if self.__manager is not None:
            # register
            for element in elements:
                element._register()
                self.__instances.append(element)

            # connect
            for element in elements:
                element._connect()

    def close(self) -> None:
        """Deregister all registered instances.
        """
        for instance in self.__instances:
            instance._deregister()

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

    def __set_up_logging(self, elements: List[ComputeElement]) -> None:
        """Adds logging handlers for one or more instances.
        """
        id_str = '-'.join([str(e._instance_name()) for e in elements])

        logfile = self.__extract_log_file_location(
                'muscle3.{}.log'.format(id_str))
        local_handler = logging.FileHandler(str(logfile), mode='w')
        logging.getLogger().addHandler(local_handler)

        if self.__manager is not None:
            mmp_handler = MuscleManagerHandler(id_str, logging.WARNING,
                                               self.__manager)
            logging.getLogger().addHandler(mmp_handler)

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

    @staticmethod
    def __extract_log_file_location(filename: str) -> Optional[Path]:
        """Gets the log file location from the command line.

        Extracts the --muscle-log-file=<path> argument to tell the
        MUSCLE library where to write the local log file. This
        function will extract this argument from the command line
        arguments if it is present. If the given path is to a
        directory, <filename> will be written inside of that directory,
        if the path is not an existing directory, then it will be used
        as the name of the log file to write to. If no command line
        argument is given, <filename> will be written in the current
        directory.

        Args:
            filename: Default file name to use.

        Returns:
            Path to the log file to write.
        """
        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix = '--muscle-log-file='
        given_path_str = ''
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                given_path_str = arg[len(prefix):]

        if given_path_str == '':
            return Path('.') / filename

        given_path = Path(given_path_str)

        if given_path.is_dir():
            return given_path / filename
        return given_path


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

    failed_processes = list()
    for instance_process in instance_processes:
        instance_process.join()
        if instance_process.exitcode != 0:
            failed_processes.append(instance_process)
    mux_process.join()

    if len(failed_processes) > 0:
        failed_names = map(lambda x: x.name, failed_processes)
        raise RuntimeError('Instances {} failed to shut down cleanly, please'
                           ' check the logs to see what went wrong.'.format(
                               ', '.join(failed_names)))
