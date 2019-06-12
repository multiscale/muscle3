import multiprocessing as mp
from typing import Callable, Dict, List, Tuple

import click
from ruamel import yaml
from ymmsl import Experiment, Reference, Simulation, YmmslDocument
import ymmsl

from libmuscle.configuration import Configuration
from libmuscle.mcp import pipe_multiplexer as mux

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.topology_store import TopologyStore


Pipe = Tuple[mp.connection.Connection, mp.connection.Connection]


def config_for_experiment(experiment: Experiment) -> Configuration:
    """Creates a Configuration from a yMMSL Experiment.

    Args:
        experiment: The experiment to create a Configuration for.
    """
    configuration = Configuration()
    if experiment.parameter_values is not None:
        for setting in experiment.parameter_values:
            configuration[setting.parameter] = setting.value
    return configuration


def elements_for_simulation(simulation: Simulation) -> List[str]:
    """Creates a list of elements to expect to register.

    Args:
        simulation: The simulation to create a list for.
    """
    def increment(index: List[int], dims: List[int]) -> None:
        # assumes index and dims are the same length > 0
        # modifies index argument
        i = len(index) - 1
        index[i] += 1
        while index[i] == dims[i]:
            index[i] = 0
            i -= 1
            if i == -1:
                break
            index[i] += 1

    def index_to_str(index: List[int]) -> str:
        result = ''
        for i in index:
            result += '[{}]'.format(i)
        return result

    def generate_indices(multiplicity: List[int]) -> List[str]:
        # n-dimensional counter
        indices = list()    # type: List[str]

        index = [0] * len(multiplicity)
        indices.append(index_to_str(index))
        increment(index, multiplicity)
        while sum(index) > 0:
            indices.append(index_to_str(index))
            increment(index, multiplicity)
        return indices

    result = list()     # type: List[str]
    for element in simulation.compute_elements:
        if len(element.multiplicity) == 0:
            result.append(str(element.name))
        else:
            for index in generate_indices(element.multiplicity):
                result.append(str(element.name) + index)
    return result


def start_server(experiment: YmmslDocument) -> MMPServer:
    """Creates an MMP server and starts it.

    Args;
        experiment: The experiment to run.
    """
    if not experiment.experiment or not experiment.simulation:
        raise RuntimeError('The yMMSL description needs to specify both an'
                           'experiment and a simulation for MUSCLE 3 to run'
                           ' it.')

    topology_store = TopologyStore(experiment)
    configuration = config_for_experiment(experiment.experiment)
    expected_elements = elements_for_simulation(experiment.simulation)

    logger = Logger()
    instance_registry = InstanceRegistry(expected_elements)
    return MMPServer(logger, configuration, instance_registry, topology_store)


class MMPServerController:
    def __init__(self, process: mp.Process, control_pipe: Pipe) -> None:
        """Create an MMPServerController.

        This class controls a manager running in a separate process.

        Args:
            pipe: The control pipe for the server process.
        """
        self._process = process
        self._control_pipe = control_pipe

    def stop(self) -> None:
        """Stop the server process.

        Tells the server to stop listening, handle any running
        requests, then quit, after which this function returns.
        """
        self._control_pipe[0].send(True)
        self._control_pipe[0].close()
        self._process.join()


def manager_process(control_pipe: Pipe, experiment: YmmslDocument) -> None:
    """Run function for a separate manager process.

    Args:
        pipe: The pipe through which to communicate with the parent.
        experiment: The experiment to run.
    """
    control_pipe[0].close()
    server = start_server(experiment)
    control_pipe[1].send(True)

    # wait for shutdown command
    control_pipe[1].recv()
    control_pipe[1].close()
    server.stop()


def start_server_process(experiment: YmmslDocument) -> MMPServerController:
    """Starts a manager in a separate process.

    Args:
        experiment: The experiment to run.

    Returns:
        A controller through which the manager can be shut down.
    """
    control_pipe = mp.Pipe()
    process = mp.Process(target=manager_process,
                         args=(control_pipe, experiment),
                         name='MuscleManager')
    process.start()
    control_pipe[1].close()
    # wait for start
    control_pipe[0].recv()

    return MMPServerController(process, control_pipe)


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


def run_simulation(experiment: YmmslDocument, instances: Dict[str, Callable]
                   ) -> None:
    """Runs a simulation with the given experiment and instances.

    The yMMSL document must contain both a simulation and an
    experiment.

    The instances are described in a dictionary with their instance
    id (e.g. 'macro' or 'micro[12]' or 'my_mapper') as the key, and
    a function to run as the corresponding value. Each instance
    will be run in a separate process.

    Args:
        experiment: A description of the simulation and experiment.
        instances: A dictionary of instances to run.
    """
    controller = start_server_process(experiment)
    run_instances(instances)
    controller.stop()


@click.command()
@click.argument('ymmsl_file')
def manage_simulation(ymmsl_file: str) -> None:

    with open(ymmsl_file) as f:
        experiment = ymmsl.load(f)

    server = start_server(experiment)
    server.wait()


if __name__ == '__main__':
    manage_simulation()
