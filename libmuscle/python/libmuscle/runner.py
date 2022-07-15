"""A simple runner for Python-only models.

Starting instances is out of scope for MUSCLE3, but is also very
useful for testing and prototyping. So we have a little bit of
support for it in this module.
"""
import logging
import multiprocessing as mp
import multiprocessing.connection as mpc
import sys
from typing import Callable, Dict, List, Tuple, cast

from ymmsl import Configuration, Identifier, Model, Reference

from libmuscle.util import generate_indices
from libmuscle.manager.manager import Manager


__all__ = ['run_simulation']


_logger = logging.getLogger(__name__)


Pipe = Tuple[mpc.Connection, mpc.Connection]


class MMPServerController:
    def __init__(
            self, process: mp.Process, control_pipe: Pipe,
            manager_location: str) -> None:
        """Create an MMPServerController.

        This class controls a manager running in a separate process.

        Args:
            process: The process the server is running in
            control_pipe: The control pipe for the server process
            manager_location: Network location of the manager
        """
        self._process = process
        self._control_pipe = control_pipe
        self.manager_location = manager_location

    def stop(self) -> None:
        """Stop the server process.

        Tells the server to stop listening, handle any running
        requests, then quit, after which this function returns.
        """
        self._control_pipe[0].send(True)
        self._control_pipe[0].close()
        self._process.join()


def manager_process(control_pipe: Pipe, configuration: Configuration) -> None:
    """Run function for a separate manager process.

    Args:
        pipe: The pipe through which to communicate with the parent.
        configuration: The configuration to run.
    """
    control_pipe[0].close()
    manager = Manager(configuration)
    control_pipe[1].send(manager.get_server_location())

    # wait for shutdown command
    control_pipe[1].recv()
    control_pipe[1].close()
    manager.stop()


def start_server_process(configuration: Configuration) -> MMPServerController:
    """Starts a manager in a separate process.

    Args:
        configuration: The configuration to run.

    Returns:
        A controller through which the manager can be shut down.
    """
    control_pipe = mp.Pipe()
    process = mp.Process(target=manager_process,
                         args=(control_pipe, configuration),
                         name='MuscleManager')
    process.start()
    control_pipe[1].close()
    # wait for start
    manager_location = control_pipe[0].recv()

    return MMPServerController(process, control_pipe, manager_location)


def implementation_process(
        instance_id: str, manager_location: str,
        implementation: Callable) -> None:
    prefix_tag = '--muscle-prefix='
    name_prefix = str()
    index_prefix = list()   # type: List[int]

    instance = Reference(instance_id)

    for i, arg in enumerate(sys.argv):
        if arg.startswith(prefix_tag):
            prefix_str = arg[len(prefix_tag):]
            name_prefix, index_prefix = _parse_prefix(prefix_str)

            name, index = _split_reference(instance)
            if len(name_prefix) > 0:
                name = Reference(name_prefix) + name
            index = index_prefix + index

            # replace it with the combined one
            sys.argv[i] = '--muscle-instance={}'.format(str(name + index))
            break
    else:
        sys.argv.append('--muscle-instance={}'.format(instance_id))

    for arg in sys.argv:
        if arg.startswith('--muscle-manager='):
            break
    else:
        sys.argv.append(f'--muscle-manager={manager_location}')

    with open(f'muscle3.{instance}.log', 'w') as log_file:
        # Redirect an already-configured standard logging setup
        # Logger.handlers and StreamHandler.stream are private, so this
        # is dangerous in theory. But this part of the logging code
        # hasn't changed in two decades, and we can use introspection to
        # avoid crashes, so in practice, it'll work.
        root_logger = logging.getLogger()
        if hasattr(root_logger, 'handlers'):
            for h in root_logger.handlers:
                if isinstance(h, logging.StreamHandler):
                    if hasattr(h, 'stream'):
                        if h.stream == sys.stderr:
                            h.stream = log_file
                        elif h.stream == sys.stdout:
                            h.stream = log_file

        sys.stderr = log_file
        sys.stdout = log_file

        # chain call
        try:
            implementation()
        except Exception:
            _logger.exception(
                    f'Component {instance} crashed, please check the log file'
                    ' for error messages')
            raise


def _parse_prefix(prefix: str) -> Tuple[str, List[int]]:
    """Parse a --muscle-prefix argument.

    This is like a Reference, but not quite, because the
    initial identifier may be omitted. That is, [1][2] is
    also a valid prefix.

    This parses an initial identifier, subsequent identifiers
    separated by periods, then a list of square-bracketed integers.

    Args:
        prefix: The prefix to parse.

    Returns:
        The identifier sequence and the list of ints.
    """
    def parse_identifier(prefix: str, i: int) -> Tuple[str, int]:
        name = str()
        while i < len(prefix) and prefix[i] not in '[.':
            name += prefix[i]
            i += 1
        return name, i

    def parse_number(prefix: str, i: int) -> Tuple[int, int]:
        number = str()
        while i < len(prefix) and prefix[i] in '0123456789':
            number += prefix[i]
            i += 1
        return int(number), i

    name = str()
    index = list()  # type: List[int]
    i = 0

    if i == len(prefix):
        return name, index

    idt, i = parse_identifier(prefix, i)
    name += idt

    while i < len(prefix) and prefix[i] == '.':
        name += '.'
        part, i = parse_identifier(prefix, i + 1)
        name += part

    while i < len(prefix) and prefix[i] == '[':
        nmb, i = parse_number(prefix, i + 1)
        index.append(nmb)
        if prefix[i] != ']':
            raise ValueError('Missing closing bracket in'
                             ' --muscle-prefix.')
        i += 1

    if i < len(prefix):
        raise ValueError(('Found invalid extra character {} in'
                          ' --muscle-prefix.').format(prefix[i]))

    return name, index


def _split_reference(ref: Reference) -> Tuple[Reference, List[int]]:
    index = list()     # type: List[int]
    i = 0
    while i < len(ref) and isinstance(ref[i], Identifier):
        i += 1
    name = ref[:i]

    while i < len(ref) and isinstance(ref[i], int):
        index.append(cast(int, ref[i]))
        i += 1

    return name, index


def run_instances(
        instances: Dict[str, Callable], manager_location: str) -> None:
    """Runs the given instances and waits for them to finish.

    The instances are described in a dictionary with their instance
    id (e.g. 'macro' or 'micro[12]' or 'my_mapper') as the key, and
    a function to run as the corresponding value. Each instance
    will be run in a separate process.

    Args:
        instances: A dictionary of instances to run
        manager_location: Network location of the manager
    """
    instance_processes = list()
    for instance_id_str, implementation in instances.items():
        instance_id = Reference(instance_id_str)
        process = mp.Process(
                target=implementation_process,
                args=(instance_id_str, manager_location, implementation),
                name='Instance-{}'.format(instance_id))
        process.start()
        instance_processes.append(process)

    failed_processes = list()
    for instance_process in instance_processes:
        instance_process.join()
        if instance_process.exitcode != 0:
            failed_processes.append(instance_process)

    if len(failed_processes) > 0:
        failed_names = map(lambda x: x.name, failed_processes)
        raise RuntimeError('Instances {} failed to shut down cleanly, please'
                           ' check the logs to see what went wrong.'.format(
                               ', '.join(failed_names)))


def run_simulation(
        configuration: Configuration, implementations: Dict[str, Callable]
        ) -> None:
    """Runs a simulation with the given configuration and instances.

    The yMMSL document must contain both a model and settings.

    This function will start the necessary instances described in
    the yMMSL document. To do so, it needs the corresponding
    implementations, which are given as a dictionary mapping the
    implementation name to a Python function (or any callable).

    Args:
        configuration: A description of the model and settings.
        instances: A dictionary of instances to run.
    """
    if not isinstance(configuration.model, Model):
        raise ValueError('The model description does not include a model'
                         ' definition, so the simulation can not be run.')

    configuration.model.check_consistent()

    instances = dict()
    for ce in configuration.model.components:
        impl_name = str(ce.implementation)
        if impl_name not in implementations:
            raise ValueError(('The model specifies an implementation named'
                              ' "{}" but the given set of implementations does'
                              ' not include it.').format(impl_name))

        impl_fn = implementations[impl_name]
        if not ce.multiplicity:
            instances[str(ce.name)] = impl_fn
        else:
            for index in generate_indices(ce.multiplicity):
                instance_id = str(ce.name + index)
                instances[instance_id] = impl_fn

    controller = start_server_process(configuration)
    try:
        run_instances(instances, controller.manager_location)
    finally:
        controller.stop()
