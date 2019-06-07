from typing import List

import click
from ruamel import yaml
from ymmsl import Experiment, Simulation
import ymmsl

from libmuscle.configuration import Configuration

from muscle_manager.instance_registry import InstanceRegistry
from muscle_manager.logger import Logger
from muscle_manager.mmp_server import MMPServer
from muscle_manager.topology_store import TopologyStore


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


@click.command()
@click.argument('ymmsl_file')
def manage_simulation(ymmsl_file: str) -> None:

    with open(ymmsl_file) as f:
        ymmsl_doc = ymmsl.load(f)

    if not ymmsl_doc.experiment or not ymmsl_doc.simulation:
        raise RuntimeError('The yMMSL file needs to specify both an experiment'
                           ' and a simulation for MUSCLE 3 to run it.')

    topology_store = TopologyStore(ymmsl_doc)
    configuration = config_for_experiment(ymmsl_doc.experiment)
    expected_elements = elements_for_simulation(ymmsl_doc.simulation)

    logger = Logger()
    instance_registry = InstanceRegistry(expected_elements)
    server = MMPServer(logger, configuration, instance_registry,
                       topology_store)
    server.wait()


if __name__ == '__main__':
    manage_simulation()
