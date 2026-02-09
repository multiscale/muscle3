from copy import deepcopy
from typing import Dict, List, Tuple

from ymmsl.v0_2 import Conduit, Configuration, Model, Ports, Reference


ConduitIndex = Dict[Reference, Tuple[Conduit, bool]]


class Plate:
    """Container for conduits during flattening.

    Models may have conduits to or from model-implemented components, and to or from
    model ports. In the flattened model, these components and ports are removed, and the
    conduits on either side merged into each other, possibly connecting together many
    conduits into a single one. The flattening algorithm does this step by step, so that
    during flattening there is a pile of partially-finished conduits lying around that
    we're working on.

    This class provides a place to keep those conduits while allowing the access
    operations we need. Why Plate? Because that's where the spaghetti goes.

    Fundamentally, this stores Conduit objects, using two indexes. One maps each
    sending endpoint to a dict keyed by receiving endpoint that in turn maps to the
    Conduit object and a bool indicating whether that receiving endpoint is on a
    program-implemented conduit and therefore final. The other one does the same, but
    the other way around, and the bool referring to the sending endpoint.
    """
    def __init__(self) -> None:
        """Create a Plate."""
        self._by_snd: Dict[Reference, ConduitIndex] = {}
        self._by_recv: Dict[Reference, ConduitIndex] = {}

    def add(self, conduit: Conduit, snd_final: bool, recv_final: bool) -> None:
        """Add a conduit to the plate.

        Args:
            conduit: The Conduit to add
            snd_final: True iff the sender is final (a program port)
            recv_final: True iff the receiver is final (a program port)
        """
        self._by_snd.setdefault(conduit.sender, {})[conduit.receiver] = (
                conduit, recv_final)
        self._by_recv.setdefault(conduit.receiver, {})[conduit.sender] = (
                conduit, snd_final)

    def pop_by_receiver(self, receiver: Reference) -> ConduitIndex:
        """Remove and return all conduits with the given receiver.

        Args:
            receiver: The receiver to search for

        Returns:
            A dictionary keyed by sender, mapping to a Conduit with that sender and the
            requested receiver, and a boolean indicating whether that sender is final.
        """
        result = self._by_recv.get(receiver, {})
        if result:
            self._by_recv[receiver] = {}

        for sender in result:
            assert not self._by_snd[sender][receiver][1]
            del self._by_snd[sender][receiver]
        return result

    def pop_by_sender(self, sender: Reference) -> ConduitIndex:
        """Remove and return all conduits with the given sender.

        Args:
            sender: The sender to search for

        Returns:
            A dictionary keyed by receiver, mapping to a Conduit with that receiver and
            the requested sender, and a boolean indicating whether that receiver is
            final.
        """
        result = self._by_snd.get(sender, {})
        if result:
            self._by_snd[sender] = {}

        for receiver in result:
            assert not self._by_recv[receiver][sender][1]
            del self._by_recv[receiver][sender]
        return result


Node = Tuple[Model, Reference, List[int]]
"""Describes a model to be processed while flattening.

This contains a model, its component path from the root, and a multiplicity.
Components inside of the model will be prefixed with the path and multiplicity before
being added to the flattened model.
"""


def apply_custom_implementations(nested_config: Configuration) -> None:
    """Applies custom implementations and removes them.

    Custom implementations are keyed by the full component path, so we need to traverse
    the hierarchy to determine that, then copy the implementation reference.

    After this, the configuration will not have any entries in custom_implementations.
    """
    root_model = nested_config.root_model()
    queue: List[Tuple[Model, Reference]] = [(root_model, Reference([]))]
    while queue:
        model, parent_path = queue.pop(0)
        for component in model.components.values():
            cmp_path = parent_path + component.name
            component.implementation = nested_config.custom_implementations.get(
                    cmp_path, component.implementation)

            if component.implementation:
                model_impl = nested_config.models.get(component.implementation)
                if model_impl:
                    queue.append((model_impl, cmp_path))

    nested_config.custom_implementations.clear()


def process_components(
        nested_config: Configuration, flat_model: Model, node: Node) -> List[Node]:
    """Copy components to the flattened model.

    This copies the components in the given model in nested_config to flat_model,
    prefixing their names with the given path and and multiplicities with the given
    multiplicity. Components that are implemented by a model are recursed into and are
    note added, and components with a None implementation are skipped and not added
    either.

    Args:
        nested_config: The nested configuration we're flattening
        flat_model: The new flat model we're creating
        node: model, parent_path, parent_mult tuple describing the model to process, the
            path to the component it implements, and the multiplicity of that component

    Returns:
        A list of new nodes to process for submodel implemented components, if any
    """
    result = list()

    model, parent_path, parent_mult = node
    for component in model.components.values():
        cmp_path = parent_path + component.name
        cmp_mult = parent_mult + component.multiplicity
        impl_ref = nested_config.custom_implementations.get(
                cmp_path, component.implementation)
        if impl_ref is None:
            continue

        if impl_ref in nested_config.models:
            result.append((nested_config.models[impl_ref], cmp_path, cmp_mult))
        else:
            new_cmp = deepcopy(component)
            new_cmp.name = cmp_path
            new_cmp.implementation = impl_ref
            new_cmp.multiplicity = cmp_mult
            flat_model.components[cmp_path] = new_cmp

    return result


def process_conduits(
        nested_config: Configuration, flat_model: Model, node: Node, plate: Plate
        ) -> None:
    """Copy flat conduits to flat model and partial conduits to plate.

    This takes the conduits from current node's model, prefixes them with its component
    path, and then adds them to the flat model if both endpoints are on
    program-implemented components in the current model. If one or both endpoints are on
    model ports, or on a model-implemented component, then the conduit is a partial one
    and gets added to the plate.

    Args:
        nested_config: The nested configuration we're flattening
        flat_model: The new flat model we're creating
        node: model, parent_path, parent_mult tuple describing the model to process, the
            path to the component it implements, and the multiplicity of that component
        plate: The plate to put partial components onto for later gluing
    """
    model, parent_path, _ = node
    for conduit in model.conduits:
        snd_cmp = conduit.sending_component()
        if snd_cmp != Reference([]):
            snd_impl = nested_config.custom_implementations.get(
                    parent_path + snd_cmp, model.components[snd_cmp].implementation)
            if snd_impl is None:
                continue
            snd_is_program = snd_impl not in nested_config.models
        else:
            snd_is_program = False

        recv_cmp = conduit.receiving_component()
        if recv_cmp != Reference([]):
            recv_impl = nested_config.custom_implementations.get(
                    parent_path + recv_cmp, model.components[recv_cmp].implementation)
            if recv_impl is None:
                continue
            recv_is_program = recv_impl not in nested_config.models
        else:
            recv_is_program = False

        prefixed_conduit = Conduit(
                str(parent_path + conduit.sender),
                str(parent_path + conduit.receiver),
                conduit.filters)
        if snd_is_program and recv_is_program:
            flat_model.conduits.append(prefixed_conduit)
        else:
            plate.add(prefixed_conduit, snd_is_program, recv_is_program)


def glue_partial_conduits(
        nested_config: Configuration, flat_model: Model, node: Node, plate: Plate
        ) -> None:
    """Glue together conduits at model ports.

    Conduits that do not lead directly from one program-implemented conduit to another
    will have at least one endpoint that ends at a model port or at a model-implemented
    component. Each port on a model-implemented component corresponds to a model port
    inside the model implementing that component, and these are the only places where
    two conduits can connect to each other.

    This function runs through all the model ports of a model-implemented component,
    gets any conduits connected to it from the outside and the inside, glues them
    together, and then adds them to the flat model if they are now complete (i.e. both
    sides connected to a program-implemented component), or puts them back onto the
    plate if they're not.

    Args:
        nested_config: The nested configuration we're flattening
        flat_model: The new flat model we're creating
        node: model, parent_path, parent_mult tuple describing the model to process, the
            path to the component it implements, and the multiplicity of that component
        plate: The plate to put partial components onto for later gluing
    """
    model, parent_path, _ = node
    ports = model.ports.receiving_port_names() + model.ports.sending_port_names()
    for port in ports:
        incoming_conduits = plate.pop_by_receiver(parent_path + port)
        outgoing_conduits = plate.pop_by_sender(parent_path + port)
        for incoming, (in_cdt, snd_final) in incoming_conduits.items():
            for outgoing, (out_cdt, recv_final) in outgoing_conduits.items():
                joined_cdt = Conduit(
                        str(in_cdt.sender), str(out_cdt.receiver),
                        in_cdt.filters + out_cdt.filters)

                if snd_final and recv_final:
                    flat_model.conduits.append(joined_cdt)
                else:
                    plate.add(joined_cdt, snd_final, recv_final)


def flatten(nested_config: Configuration) -> Configuration:
    """Creates a flat version of the given configuration.

    The result will have a single model, without any components that have a model for
    their implementation, or that do not have an implementation, and with the remaining
    components with their full name (path from the root model). Conduits will be merged
    and removed accordingly, and custom implementations applied.

    This does a breadth-first traverse through model-implemented components, starting
    from the root model and a virtual component with an empty name and multiplicity. As
    it recurses downward, it accumulates component names and multiplicities.

    Program-implemented components inside of the processed model-implemnted components
    have their names and implementations prefixed with those of the parent component,
    and conduits between them have their endpoints updated accordingly. Finally,
    components leading into and out of submodels are glued together and added as well.

    Args:
        nested_configuration: A complete, consistent, (potentially) nested
            configuration.

    Returns:
        A copy of that configuration, modified to contain only a single flat model
        corresponding to the input, with no custom_implementations.
    """
    config = deepcopy(nested_config)

    plate = Plate()
    root_model = config.root_model()
    flat_model = Model(
            str(root_model.name), Ports(), root_model.description,
            root_model.supported_settings, [], [])

    apply_custom_implementations(config)

    queue: List[Node] = [(root_model, Reference([]), [])]
    while queue:
        node = queue.pop(0)
        queue.extend(process_components(config, flat_model, node))
        process_conduits(config, flat_model, node, plate)
        glue_partial_conduits(config, flat_model, node, plate)

    config.models = {flat_model.name: flat_model}

    return config
