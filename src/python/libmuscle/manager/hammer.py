from copy import copy, deepcopy
from dataclasses import dataclass

from ymmsl.v0_2 import (
    Conduit,
    Configuration,
    Identifier,
    MatchingTimelines,
    Model,
    Ports,
    Reference,
    Timeline,
)

ConduitIndex = dict[Reference, tuple[Conduit, bool]]


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
        self._by_snd: dict[Reference, ConduitIndex] = {}
        self._by_recv: dict[Reference, ConduitIndex] = {}

    def add(self, conduit: Conduit, snd_final: bool, recv_final: bool) -> None:
        """Add a conduit to the plate.

        Args:
            conduit: The Conduit to add
            snd_final: True iff the sender is final (a program port)
            recv_final: True iff the receiver is final (a program port)
        """
        self._by_snd.setdefault(conduit.sender, {})[conduit.receiver] = (
            conduit,
            recv_final,
        )
        self._by_recv.setdefault(conduit.receiver, {})[conduit.sender] = (
            conduit,
            snd_final,
        )

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


class History:
    """Container for matching timelines during flattening.

    This keeps track of which timelines have been declared to match, expanding the
    groups of matching timelines as new matches are processed.

    Many Timelines make a History
    """

    def __init__(self) -> None:
        """Create a History."""
        self.matching_timelines: set[MatchingTimelines] = set()

    def add(self, matching_timelines: MatchingTimelines) -> None:
        """Add the given matching timelines.

        If any timeline in matching_timelines is also in another MatchingTimelines
        object currently in this History, then the groups will be merged into one.
        """
        matching_sets = set()
        for timeline in matching_timelines.matches:
            for mt in self.matching_timelines:
                if timeline in mt.matches:
                    matching_sets.add(mt)

        merged_matches = copy(matching_timelines)
        for ms in matching_sets:
            merged_matches |= ms

        self.matching_timelines -= matching_sets
        self.matching_timelines.add(merged_matches)


@dataclass
class Node:
    """Describes a submodel to be processed while flattening.

    This contains the path of the component we're processing, the model implementing it,
    the timeline on which it will run, and its multiplicity.
    """

    parent_path: Reference
    model: Model
    parent_timeline: Timeline
    parent_multiplicity: list[int]


def double_prefix(
    timeline: Timeline, parent_path: Reference, parent_timeline: Timeline
) -> Timeline:
    """Prefix a timeline with a parent path and a parent timeline.

    This prefixes every Reference in the timeline with the parent path, thus applying
    the model nesting hierarchy, and then prepends the given parent timeline, thus
    applying the call hierarchy.
    """
    new_timeline = Timeline([parent_path + part for part in timeline])
    return parent_timeline + new_timeline


def process_components(
    nested_config: Configuration, flat_model: Model, node: Node
) -> list[Node]:
    """Copy components to the flattened model.

    This copies the components in the given model in nested_config to flat_model,
    prefixing names, timelines, and multiplicity with the parents in node. Components
    that are implemented by a model are returned for recursing into later and are not
    added, and components with a None implementation are skipped and not added either.

    Args:
        nested_config: The nested configuration we're flattening
        flat_model: The new flat model we're creating
        node: Node describing the model-implemented component to process

    Returns:
        A list of new nodes to process for submodel implemented components, if any
    """
    result = list()

    for component in node.model.components.values():
        if component.timeline is None:
            raise RuntimeError("Trying to flatten without resolving timelines first")
        cmp_path = node.parent_path + component.name
        cmp_timeline = double_prefix(
            component.timeline, node.parent_path, node.parent_timeline
        )
        cmp_mult = node.parent_multiplicity + component.multiplicity
        impl_ref = nested_config.custom_implementations.get(
            cmp_path, component.implementation
        )
        if impl_ref is None:
            continue

        if impl_ref in nested_config.models:
            result.append(
                Node(
                    cmp_path,
                    nested_config.models[impl_ref],
                    cmp_timeline[:-1],
                    cmp_mult,
                )
            )
        else:
            new_cmp = deepcopy(component)
            new_cmp.name = cmp_path
            new_cmp.implementation = impl_ref
            new_cmp.multiplicity = cmp_mult
            new_cmp.timeline = cmp_timeline
            flat_model.components[cmp_path] = new_cmp

    return result


def _timeline_for_port(node: Node, port_ref: Reference) -> Timeline:
    """Create the prefixed timeline of a port given a reference to it."""
    cmp_name = port_ref[:-1]
    port_name = port_ref[-1]
    assert isinstance(port_name, Identifier)
    if cmp_name == Reference([]):
        if port_name in node.model.ports:
            port = node.model.ports[port_name]
            if port.timeline:
                timeline = double_prefix(
                    port.timeline, node.parent_path, node.parent_timeline
                )
            else:
                timeline = node.parent_timeline + Timeline([node.parent_path])
        else:
            raise RuntimeError(
                f"Model port {port_name} not found in model {node.model.name}"
            )
    else:
        if cmp_name in node.model.components:
            component = node.model.components[cmp_name]
            assert component.timeline is not None
            if port_name in component.ports:
                port = component.ports[port_name]
                timeline = double_prefix(
                    component.timeline, node.parent_path, node.parent_timeline
                )
                if port.timeline:
                    timeline = timeline[:-1] + (timeline[-1] + port.timeline[0])

            else:
                if port_name == "muscle_settings_in":
                    timeline = double_prefix(
                        component.timeline, node.parent_path, node.parent_timeline
                    )
                else:
                    raise RuntimeError(
                        f"Port {port_name} not found on component {cmp_name}"
                    )
        else:
            raise RuntimeError(
                f"Component {cmp_name} not found in model {node.model.name}"
            )

    return timeline


def process_matching_timelines(
    nested_config: Configuration, node: Node, history: History
) -> None:
    """Copy matching timelines into history, while prefixing.

    This take the matching timelines from the current model, prefixes them with the
    current namespace and timeline prefixes, and merges them into the history. It then
    also generates an entry for each conduit attached to a model port, declaring the
    timelines on either side of that conduit to match.

    Args:
        nested_config: The nested configuration we're flattening
        node: Node to process
        history: The history to put the matches into for later use in the flat
            model
    """

    if node.model.matching_timelines:
        for mt in node.model.matching_timelines:
            prefixed_matches = [
                double_prefix(tl, node.parent_path, node.parent_timeline)
                for tl in mt.matches
            ]
            prefixed_head = double_prefix(
                mt.head, node.parent_path, node.parent_timeline
            )
            history.add(MatchingTimelines(prefixed_head, prefixed_matches))

    for conduit in node.model.conduits:
        if not conduit.sending_component() or not conduit.receiving_component():
            pfx_snd_tl = _timeline_for_port(node, conduit.sender)
            pfx_recv_tl = _timeline_for_port(node, conduit.receiver)
            history.add(MatchingTimelines(pfx_snd_tl, [pfx_recv_tl]))


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
        node: Node to process conduits for
        plate: The plate to put partial components onto for later gluing
    """
    for conduit in node.model.conduits:
        snd_cmp = conduit.sending_component()
        if snd_cmp != Reference([]):
            snd_impl = nested_config.custom_implementations.get(
                node.parent_path + snd_cmp,
                node.model.components[snd_cmp].implementation,
            )
            if snd_impl is None:
                continue
            snd_is_program = snd_impl not in nested_config.models
        else:
            snd_is_program = False

        recv_cmp = conduit.receiving_component()
        if recv_cmp != Reference([]):
            recv_impl = nested_config.custom_implementations.get(
                node.parent_path + recv_cmp,
                node.model.components[recv_cmp].implementation,
            )
            if recv_impl is None:
                continue
            recv_is_program = recv_impl not in nested_config.models
        else:
            recv_is_program = False

        prefixed_conduit = Conduit(
            str(node.parent_path + conduit.sender),
            str(node.parent_path + conduit.receiver),
            conduit.filters,
        )
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
        node: Node to glue conduits for
        plate: The plate to put partial components onto for later gluing
    """
    ports = (
        node.model.ports.receiving_port_names() + node.model.ports.sending_port_names()
    )
    for port in ports:
        incoming_conduits = plate.pop_by_receiver(node.parent_path + port)
        outgoing_conduits = plate.pop_by_sender(node.parent_path + port)
        for in_cdt, snd_final in incoming_conduits.values():
            for out_cdt, recv_final in outgoing_conduits.values():
                joined_cdt = Conduit(
                    str(in_cdt.sender),
                    str(out_cdt.receiver),
                    in_cdt.filters + out_cdt.filters,
                )

                if snd_final and recv_final:
                    flat_model.conduits.append(joined_cdt)
                else:
                    plate.add(joined_cdt, snd_final, recv_final)


def flatten(
    nested_config: Configuration, model: Reference | None = None
) -> Configuration:
    """Creates a flat version of the given configuration.

    The result will have a single model, without any components that have a model for
    their implementation, or that do not have an implementation, and with the remaining
    components with their full name (path from the root model). Conduits will be merged
    and removed accordingly, and custom implementations applied.

    This does a breadth-first traverse through model-implemented components, starting
    from the root model and a virtual component with an empty name and multiplicity. As
    it recurses downward, it accumulates component names and multiplicities.

    Program-implemented components inside of the processed model-implemented components
    have their names and implementations prefixed with those of the parent component,
    and conduits between them have their endpoints updated accordingly. Finally,
    components leading into and out of submodels are glued together and added as well.

    Args:
        nested_configuration: A complete, consistent, (potentially) nested
            configuration.
        model: Root model to start from

    Returns:
        A copy of that configuration, modified to contain only a single flat model
        corresponding to the input, with no custom_implementations.
    """
    config = deepcopy(nested_config)

    plate = Plate()
    history = History()
    root_model = config.root_model(model)
    flat_model = Model(
        str(root_model.name),
        Ports(),
        root_model.description,
        root_model.supported_settings,
        [],
        [],
    )

    queue: list[Node] = [Node(Reference([]), root_model, Timeline(""), [])]
    while queue:
        node = queue.pop(0)
        queue.extend(process_components(config, flat_model, node))
        process_matching_timelines(config, node, history)
        process_conduits(config, flat_model, node, plate)
        glue_partial_conduits(config, flat_model, node, plate)

    flat_model.matching_timelines = list(history.matching_timelines)
    config.models = {flat_model.name: flat_model}

    return config
