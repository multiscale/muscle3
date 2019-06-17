from typing import Dict, List

from ymmsl import Conduit, Configuration, Model, Reference


class TopologyStore:
    """Holds a description of how the simulation is wired together.

    This class contains the list of conduits through which the
    submodels are connected.

    Attributes:
        conduits (List[Conduit]): A list of conduits.
    """
    def __init__(self, config: Configuration) -> None:
        """Creates a TopologyStore.

        Creates a TopologyStore containing conduits read from the given
        configuration data, which must contain a 'model' key.

        Args:
            configuration: A yMMSL configuration.
        """
        if config.model is None or not isinstance(config.model, Model):
            raise ValueError('The yMMSL experiment description does not'
                             ' contain a (complete) model section, so there'
                             ' is nothing to run!')
        self.conduits = config.model.conduits
        self.kernel_dimensions = {
                k.name: k.multiplicity
                for k in config.model.compute_elements}

    def has_kernel(self, kernel: Reference) -> bool:
        """Returns True iff the given kernel is in the model.

        Args:
            kernel: The kernel to check for.
        """
        return kernel in self.kernel_dimensions

    def get_conduits(self, kernel_name: Reference) -> List[Conduit]:
        """Returns the list of conduits that attach to the given kernel.

        Args:
            kernel_name: Name of the kernel.

        Returns:
            All conduits that this kernel is a sender or receiver of.
        """
        ret = list()
        for conduit in self.conduits:
            if conduit.sending_compute_element() == kernel_name:
                ret.append(conduit)
            if conduit.receiving_compute_element() == kernel_name:
                ret.append(conduit)
        return ret

    def get_peer_dimensions(self, kernel_name: Reference
                            ) -> Dict[Reference, List[int]]:
        """Returns the dimensions of peer kernels.

        For each kernel that the given kernel shares a conduit with,
        the returned dictionary has an entry containing its dimensions.

        Args:
            kernel_name: Name of the kernel for which to get peers.

        Returns:
            A dict of peer kernels and their dimensions.
        """
        ret = dict()
        for conduit in self.conduits:
            if conduit.sending_compute_element() == kernel_name:
                recv = conduit.receiving_compute_element()
                ret[recv] = self.kernel_dimensions[recv]
            if conduit.receiving_compute_element() == kernel_name:
                snd = conduit.sending_compute_element()
                ret[snd] = self.kernel_dimensions[snd]
        return ret
