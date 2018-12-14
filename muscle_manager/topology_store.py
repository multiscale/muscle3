from ruamel import yaml
from ymmsl import Conduit, loader


class TopologyStore:
    """Holds a description of how the simulation is wired together.

    This class contains the list of conduits through which the
    submodels are connected.

    Attributes:
        conduits (List[Conduit]): A list of conduits.
    """
    def __init__(self, ymmsl_text: str) -> None:
        """Creates a TopologyStore.

        Creates a TopologyStore containing conduits read from the given
        yMMSL data, which must contain a 'simulation' key.

        Args:
            ymmsl_data: A yMMSL file, in string form.
        """
        ymmsl = yaml.load(ymmsl_text, Loader=loader)
        if ymmsl.simulation is None:
            raise ValueError('The yMMSL simulation description does not'
                             ' contain a simulation section, so there'
                             ' is nothing to run!')
        self.conduits = ymmsl.simulation.conduits
