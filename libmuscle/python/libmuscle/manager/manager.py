from typing import List

from ymmsl import Configuration, Model

from libmuscle.manager.instance_registry import InstanceRegistry
from libmuscle.manager.logger import Logger
from libmuscle.manager.mmp_server import MMPServer
from libmuscle.manager.topology_store import TopologyStore


def elements_for_model(model: Model) -> List[str]:
    """Creates a list of elements to expect to register.

    Args:
        model: The model to create a list for.
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
    for element in model.components:
        if len(element.multiplicity) == 0:
            result.append(str(element.name))
        else:
            for index in generate_indices(element.multiplicity):
                result.append(str(element.name) + index)
    return result


def start_server(configuration: Configuration) -> MMPServer:
    """Creates an MMP server and starts it.

    Args;
        configuration: The configuration to run.
    """
    if configuration.settings is None:
        raise ValueError('The yMMSL description needs to specify the'
                         ' settings for the simulation.')
    if not configuration.model or not isinstance(configuration.model, Model):
        raise ValueError('The yMMSL description needs to specify the'
                         ' model to run.')

    topology_store = TopologyStore(configuration)
    expected_elements = elements_for_model(configuration.model)

    logger = Logger()
    instance_registry = InstanceRegistry(expected_elements)
    return MMPServer(logger, configuration.settings, instance_registry,
                     topology_store)
