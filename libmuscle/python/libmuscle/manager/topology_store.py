from ymmsl.v0_2 import Conduit, Configuration, Ports, Reference

from libmuscle.util import generate_indices, instance_indices


class TopologyStore:
    """Holds a description of how the simulation is wired together.

    This class contains the list of conduits through which the
    submodels are connected.

    Attributes:
        conduits (list[Conduit]): A list of conduits.
    """
    def __init__(self, config: Configuration) -> None:
        """Creates a TopologyStore.

        Creates a TopologyStore containing conduits read from the given configuration
        data, which is expected to contain a single model

        Args:
            configuration: A yMMSL configuration.
        """
        self.model = config.root_model()

    def has_component(self, component: Reference) -> bool:
        """Returns True iff the given component is in the model.

        Args:
            component: The component to check for.
        """
        return component in self.model.components

    def get_conduits(self, component: Reference) -> list[Conduit]:
        """Returns the list of conduits that attach to the given component.

        Args:
            component: Name of the component.

        Returns:
            All conduits that this component is a sender or receiver of.
        """
        ret = list()
        for conduit in self.model.conduits:
            if conduit.sending_component() == component:
                ret.append(conduit)
            if conduit.receiving_component() == component:
                ret.append(conduit)
        return ret

    def get_ports(self, component: Reference) -> Ports:
        """Returns the port declaration (from the yMMSL) for a component.

        Args:
            component: The component to request the ports from.

        Returns:
            The port declaration in the yMMSL (from the model/components section).
        """
        return self.model.components[component].ports

    def get_peer_dimensions(self, component: Reference
                            ) -> dict[Reference, list[int]]:
        """Returns the dimensions of peer components.

        For each component that the given component shares a conduit with,
        the returned dictionary has an entry containing its dimensions.

        Args:
            component: Name of the component for which to get peers.

        Returns:
            A dict of peer components and their dimensions.
        """
        ret = dict()
        for conduit in self.model.conduits:
            if conduit.sending_component() == component:
                recv = conduit.receiving_component()
                ret[recv] = self.model.components[recv].multiplicity
            if conduit.receiving_component() == component:
                snd = conduit.sending_component()
                ret[snd] = self.model.components[snd].multiplicity
        return ret

    def get_peer_instances(self, instance: Reference) -> list[Reference]:
        """Generates the names of all peer instances of an instance.

        Args:
            instance: The instance whose peers to generate.

        Returns:
            All peer instance identifiers.
        """
        component = instance.without_trailing_ints()
        indices = instance_indices(instance)
        dims = self.model.components[component].multiplicity
        all_peer_dims = self.get_peer_dimensions(component)

        peers = []
        for peer, peer_dims in all_peer_dims.items():
            base = peer
            for i in range(min(len(dims), len(peer_dims))):
                base += indices[i]

            if dims >= peer_dims:
                peers.append(base)
            else:
                for peer_indices in generate_indices(peer_dims[len(dims):]):
                    peers.append(base + peer_indices)
        return peers
