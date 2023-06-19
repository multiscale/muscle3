from copy import copy, deepcopy
import logging
from typing import Dict, Iterable, List, Mapping, Optional, Set, Tuple

from ymmsl import (
        Component, Configuration, Model, MPICoresResReq, MPINodesResReq,
        Operator, Reference, ResourceRequirements, ThreadedResReq)

from libmuscle.util import instance_indices


_logger = logging.getLogger(__name__)


_PredSuccType = Dict[Component, Set[Tuple[Component, int]]]


class ModelGraph:
    """Represents a yMMSL model as a graph."""
    def __init__(self, model: Model) -> None:
        """Create a ModelGraph.

        This is essentially a helper class that makes it easier to
        analyse a yMMSL model definition.

        Args:
            model: The model to represent.
        """
        self._model = model

        self._direct_superpreds: _PredSuccType = {}
        self._direct_predecessors: _PredSuccType = {}
        self._direct_subpreds: _PredSuccType = {}

        self._direct_supersuccs: _PredSuccType = {}
        self._direct_successors: _PredSuccType = {}
        self._direct_subsuccs: _PredSuccType = {}

        self._superpreds: _PredSuccType = {}
        self._predecessors: _PredSuccType = {}
        self._subpreds: _PredSuccType = {}

        self._supersuccs: _PredSuccType = {}
        self._successors: _PredSuccType = {}
        self._subsuccs: _PredSuccType = {}

        self._calc_direct_succs_preds()
        self._calc_predecessors()
        self._calc_successors()

    def components(self) -> Iterable[Component]:
        """Return the components of the model (nodes)."""
        return self._model.components

    def component(self, name: Reference) -> Component:
        """Return a component by name.

        Args:
            name: Name of the component to look up

        Returns:
            The component with the given name

        Raises:
            KeyError: If no component could be found
        """
        for component in self._model.components:
            if component.name == name:
                return component
        raise KeyError('Component {} not found'.format(name))

    def successors(self, component: Component) -> Set[Tuple[Component, int]]:
        """Return the successors of the given component.

        Args:
            component: The reference component

        Returns:
            The set of components for which a path exists from
            component's O_F to their F_INIT.

        Raises:
            KeyError: If the component is not in the model used to
                construct this object.
        """
        return self._successors[component]

    def predecessors(self, component: Component) -> Set[Tuple[Component, int]]:
        """Return the predecessors of the given component.

        Args:
            component: The reference component

        Returns:
            The set of components for which a path exists from
            their O_F to component's F_INIT.

        Raises:
            KeyError: If the component is not in the model used to
                construct this object.
        """
        return self._predecessors[component]

    def macros(self, component: Component) -> Set[Tuple[Component, int]]:
        """Return the macros of the given component.

        These are components that are both before the component's
        F_INIT and after its O_F.

        Args:
            component: The reference component

        Returns:
            The set of components that are both super-predecessor
            and super-successor of component.
        """
        return self._superpreds[component] & self._supersuccs[component]

    def micros(self, component: Component) -> Set[Tuple[Component, int]]:
        """Return the micros of the given component.

        These are components that are in between the component's
        O_I and its S.

        Args:
            component: The reference component

        Returns:
            The set of components that are both sub-successor
            and sub-predecessor of component.
        """
        return self._subsuccs[component] & self._subpreds[component]

    def _propagate(
            self, from_set: Set[Tuple[Component, int]],
            to_set: Set[Tuple[Component, int]], shared_dims: int
            ) -> None:
        """Propagates from_set into to_set.

        Note: Modifies to_set.

        Args:
            from_set: Set to propagate components from
            to_set: Set to propagate them into
            shared_dims: Maximum shared dimensions to carry
        """
        to_set.update({
            (cmp, min(sd, shared_dims))
            for cmp, sd in from_set})

    def _calc_predecessors(self) -> None:
        """Calculates predecessors of each component in the model.

        This function determines for each component in the model which
        other components can be reached by following incoming conduits.

        Preconditions:
            self._model set
            self._direct_* calculated

        Side effects:
            Fills self._superpreds, self._predecessors, self._subpreds
            with for each component in the model the corresponding set
            of components.
        """
        self._superpreds = {c: set() for c in self._model.components}
        self._predecessors = {c: set() for c in self._model.components}
        self._subpreds = {c: set() for c in self._model.components}

        num_remaining_preds = {
                c: (
                    len(self._direct_predecessors[c]) +
                    len(self._direct_superpreds[c]))
                for c in self._model.components}
        num_remaining_subpreds = {
                c: len(self._direct_subpreds[c])
                for c in self._model.components}

        todo = set(self._model.components)
        started: Set[Component] = set()
        doing: Set[Component] = set()
        finished: Set[Component] = set()
        done: Set[Component] = set()
        while todo or doing:
            started.clear()
            for component in todo:
                if num_remaining_preds[component] == 0:
                    for subsucc, shared_dims in self._direct_subsuccs[component]:
                        self._superpreds[subsucc].add((component, shared_dims))
                        self._propagate(
                                self._predecessors[component],
                                self._predecessors[subsucc], shared_dims)

                        self._propagate(
                                self._superpreds[component],
                                self._superpreds[subsucc], shared_dims)

                        num_remaining_preds[subsucc] -= 1
                    started.add(component)

            todo -= started
            doing |= started

            finished.clear()
            for component in doing:
                if num_remaining_subpreds[component] == 0:
                    for succ, shared_dims in self._direct_successors[component]:
                        self._predecessors[succ].add((component, shared_dims))
                        self._propagate(
                                self._subpreds[component],
                                self._predecessors[succ], shared_dims)

                        self._propagate(
                                self._predecessors[component],
                                self._predecessors[succ], shared_dims)

                        self._propagate(
                                self._superpreds[component],
                                self._superpreds[succ], shared_dims)

                        num_remaining_preds[succ] -= 1

                    for supersucc, shared_dims in self._direct_supersuccs[component]:
                        self._subpreds[supersucc].add((component, shared_dims))

                        self._propagate(
                                self._subpreds[component],
                                self._subpreds[supersucc], shared_dims)

                        self._propagate(
                                self._predecessors[component],
                                self._subpreds[supersucc], shared_dims)

                        num_remaining_subpreds[supersucc] -= 1

                    finished.add(component)

            doing -= finished
            done |= finished

            if not started and not finished:
                raise RuntimeError(
                        'Could not plan resource allocation for this model.'
                        ' Do you have a cycle of O_F -> F_INIT conduits?'
                        ' That does not work, because the models will all be'
                        ' waiting for each other to start.')

    def _calc_successors(self) -> None:
        """Calculates successors of each component in the model.

        This function determines for each component in the model which
        other components can be reached by following outgoing conduits.

        Preconditions:
            self._model set
            self._direct_* calculated

        Side effects:
            Fills self._supersuccs, self._successors, self._subsuccs
            with for each component in the model the corresponding set
            of components.
        """
        self._supersuccs = {c: set() for c in self._model.components}
        self._successors = {c: set() for c in self._model.components}
        self._subsuccs = {c: set() for c in self._model.components}

        num_remaining_succs = {
                c: (
                    len(self._direct_successors[c]) +
                    len(self._direct_supersuccs[c]))
                for c in self._model.components}

        num_remaining_subsuccs = {
                c: len(self._direct_subsuccs[c])
                for c in self._model.components}

        todo = set(self._model.components)
        started: Set[Component] = set()
        doing: Set[Component] = set()
        finished: Set[Component] = set()
        done: Set[Component] = set()
        while todo or doing:
            started.clear()
            for component in todo:
                if num_remaining_succs[component] == 0:
                    for subpred, shared_dims in self._direct_subpreds[component]:
                        self._supersuccs[subpred].add((component, shared_dims))
                        self._propagate(
                                self._successors[component],
                                self._successors[subpred], shared_dims)

                        self._propagate(
                                self._supersuccs[component],
                                self._supersuccs[subpred], shared_dims)
                        num_remaining_succs[subpred] -= 1

                    started.add(component)

            todo -= started
            doing |= started

            finished.clear()
            for component in doing:
                if num_remaining_subsuccs[component] == 0:
                    for pred, shared_dims in self._direct_predecessors[component]:
                        self._successors[pred].add((component, shared_dims))
                        self._propagate(
                                self._successors[component],
                                self._successors[pred], shared_dims)

                        self._propagate(
                                self._supersuccs[component],
                                self._supersuccs[pred], shared_dims)

                        self._propagate(
                                self._subsuccs[component],
                                self._successors[pred], shared_dims)
                        num_remaining_succs[pred] -= 1

                    for superpred, shared_dims in self._direct_superpreds[component]:
                        self._subsuccs[superpred].add((component, shared_dims))
                        self._propagate(
                                self._successors[component],
                                self._subsuccs[superpred], shared_dims)

                        self._propagate(
                                self._subsuccs[component],
                                self._subsuccs[superpred], shared_dims)
                        num_remaining_subsuccs[superpred] -= 1
                    finished.add(component)

            doing -= finished
            done |= finished

    def _calc_direct_succs_preds(self) -> None:
        """Calculates all successors and predecessors of components.

        Preconditions:
            self._model set

        Side effects:
            Sets self._direct_successors to a dictionary mapping each
            component in the model to the set of components that it
            has a * -> F_INIT conduit to.
        """
        components = {c.name: c for c in self._model.components}
        self._direct_supersuccs = {c: set() for c in self._model.components}
        self._direct_successors = {c: set() for c in self._model.components}
        self._direct_subsuccs = {c: set() for c in self._model.components}
        self._direct_superpreds = {c: set() for c in self._model.components}
        self._direct_predecessors = {c: set() for c in self._model.components}
        self._direct_subpreds = {c: set() for c in self._model.components}

        for conduit in self._model.conduits:
            sender = components[conduit.sending_component()]
            snd_op = None
            if sender.ports:
                if conduit.sending_port() in sender.ports.o_i:
                    snd_op = Operator.O_I
                elif conduit.sending_port() in sender.ports.o_f:
                    snd_op = Operator.O_F

            receiver = components[conduit.receiving_component()]
            recv_op = None
            if conduit.receiving_port() == 'muscle_settings_in':
                recv_op = Operator.F_INIT
            elif receiver.ports:
                if conduit.receiving_port() in receiver.ports.f_init:
                    recv_op = Operator.F_INIT
                elif conduit.receiving_port() in receiver.ports.s:
                    recv_op = Operator.S

            shared_dims = min(len(sender.multiplicity), len(receiver.multiplicity))

            if (snd_op, recv_op) == (Operator.O_I, Operator.F_INIT):
                self._direct_superpreds[receiver].add((sender, shared_dims))
                self._direct_subsuccs[sender].add((receiver, shared_dims))
            elif (snd_op, recv_op) == (Operator.O_F, Operator.F_INIT):
                self._direct_successors[sender].add((receiver, shared_dims))
                self._direct_predecessors[receiver].add((sender, shared_dims))
            elif (snd_op, recv_op) == (Operator.O_F, Operator.S):
                self._direct_subpreds[receiver].add((sender, shared_dims))
                self._direct_supersuccs[sender].add((receiver, shared_dims))


class Resources:
    """Designates a (sub)set of resources.

    Whether these resources are free or allocated in general or by
    something specific depends on the context, this just says which
    resources we're talking about.

    Attributes:
        cores: A dictionary mapping designated nodes to designated
                cores on them.
    """
    def __init__(self, cores: Optional[Dict[str, Set[int]]] = None) -> None:
        """Create a Resources object with the given cores.

        Args:
            cores: Cores to be designated by this object.
        """
        if cores is None:
            self.cores: Dict[str, Set[int]] = {}
        else:
            self.cores = cores

    def __copy__(self) -> 'Resources':
        """Copy the object."""
        return Resources(deepcopy(self.cores))

    def __eq__(self, other: object) -> bool:
        """Check for equality."""
        if not isinstance(other, Resources):
            return NotImplemented

        if len(self.cores) != len(other.cores):
            return False

        for node, cores in self.cores.items():
            if node not in other.cores:
                return False
            if other.cores[node] != cores:
                return False
        return True

    def __iadd__(self, other: 'Resources') -> 'Resources':
        """Add the resources in the argument to this object."""
        for node in other.cores:
            if node in self.cores:
                self.cores[node] |= other.cores[node]
            else:
                self.cores[node] = set(other.cores[node])
        return self

    def __isub__(self, other: 'Resources') -> 'Resources':
        """Remove the resources in the argument from this object."""
        for node in other.cores:
            if node in self.cores:
                self.cores[node] -= other.cores[node]
                if not self.cores[node]:
                    del self.cores[node]
        return self

    def __str__(self) -> str:
        """Return a human-readable string representation."""
        def collapse_ranges(cores: Set[int]) -> str:
            if len(cores) == 0:
                return ''

            result = list()
            scores = sorted(cores)
            start = 0
            i = 1
            while i <= len(scores):
                if (i == len(scores)) or (scores[i-1] != scores[i] - 1):
                    if start == i - 1:
                        # run of one
                        result.append(str(scores[i-1]))
                    else:
                        # run of at least two
                        result.append(f'{scores[start]}-{scores[i-1]}')
                    start = i
                i += 1
            return ','.join(result)

        return 'Resources(' + '; '.join([
            n + ': ' + collapse_ranges(cs)
            for n, cs in self.cores.items()]) + ')'

    def __repr__(self) -> str:
        """Return a string representation."""
        return f'Resources({self.cores})'

    def nodes(self) -> Iterable[str]:
        """Returns the nodes on which we designate resources."""
        return self.cores.keys()

    def total_cores(self) -> int:
        """Returns the total number of cores designated."""
        return sum([len(cs) for cs in self.cores.values()])

    def isdisjoint(self, other: 'Resources') -> bool:
        """Returns whether we share resources with other."""
        for node, cores in self.cores.items():
            if node in other.cores:
                if not cores.isdisjoint(other.cores[node]):
                    return False
        return True

    @staticmethod
    def union(resources: Iterable['Resources']) -> 'Resources':
        """Combines the resources into one.

        Args:
            resources: A collection of resources to merge.

        Return:
            A Resources object referring to all the resources in the
            input.
        """
        result = Resources()
        for cur_resources in resources:
            result += cur_resources
        return result


class InsufficientResourcesAvailable(RuntimeError):
    pass


class Planner:
    """Allocates resources and keeps track of allocations."""
    def __init__(self, all_resources: Resources):
        """Create a ResourceManager.

        Args:
            all_resources: An object describing the available resources
                    to be managed by this ResourceManager.
        """
        self._all_resources = all_resources
        self._allocations: Dict[Reference, Resources] = {}
        self._oversubscribed: Dict[Reference, Resources] = {}
        self._next_virtual_node = 1

    def allocate_all(
            self, configuration: Configuration, virtual: bool = False
            ) -> Dict[Reference, Resources]:
        """Allocates resources for the given components.

        Allocation can occur either on a fixed set of available
        resources (virtual set to  False), or on an elastic set of
        virtual resources (virtual set to True). Use the former
        inside of a (fixed) cluster allocation and the latter to
        determine how many nodes are needed to run a simulation
        without oversubscribing.

        If virtual is True, additional nodes will be added as
        needed to obtain the resources needed to allocate all
        instances. Each additional node will have as many cores
        as a random existing one. The intended use is to pass a
        single node to __init__ when using this mode.

        Args:
            configuration: Configuration to allocate all components of
            virtual: Allocate on virtual resources or not, see above

        Returns:
            Resources for each instance required by the model.
        """
        result: Dict[Reference, Resources] = {}

        # Analyse model
        model = ModelGraph(configuration.model)
        requirements = configuration.resources
        implementations = configuration.implementations
        exclusive = {
                i for c in model.components() for i in c.instances()
                if (c.implementation and
                    not implementations[c.implementation].can_share_resources)}

        # Allocate
        unallocated_instances = [
                i for c in model.components() for i in c.instances()]
        leftover_instances: List[Reference] = []
        while unallocated_instances:
            leftover_instances.clear()

            to_allocate = self._sort_instances(
                    unallocated_instances, requirements)

            for instance in to_allocate:
                component = model.component(instance.without_trailing_ints())
                conflicting_names = self._conflicting_names(
                        model, exclusive, component, instance)

                done = False
                while not done:
                    try:
                        result[instance] = self._allocate_instance(
                                instance, component,
                                requirements[component.name],
                                conflicting_names, virtual)
                        done = True
                    except InsufficientResourcesAvailable:
                        if virtual:
                            self._expand_resources(
                                    component.name,
                                    requirements[component.name])
                        else:
                            leftover_instances.append(instance)
                            done = True

            if leftover_instances:
                _logger.warning(
                    'Planner ran out of resources, oversubscribing remaining'
                    ' instances.')
                self._oversubscribed.update(self._allocations)
                self._allocations.clear()

            unallocated_instances.clear()
            unallocated_instances.extend(leftover_instances)

        return result

    def _sort_instances(
            self, instances: List[Reference],
            requirements: Mapping[Reference, ResourceRequirements]
            ) -> List[Reference]:
        """Return to be allocated components in optimal order.

        This is a heuristic, it's not actually optimal but it should
        give decent results most of the time.

        Args:
            instances: The instances to sort
            requirements: The resource requirements for their
                components, indexed by name
        """
        cmp_names = map(Reference.without_trailing_ints, instances)
        reqs = map(lambda n: requirements[n], cmp_names)
        instances_reqs = list(zip(instances, reqs))
        threaded = [
                (i, r.threads) for i, r in instances_reqs
                if isinstance(r, ThreadedResReq)]
        sorted_threaded = sorted(threaded, key=lambda x: x[1], reverse=True)
        sorted_threaded_instances = [x[0] for x in sorted_threaded]

        mpi = [
                (i, r.mpi_processes) for i, r in instances_reqs
                if isinstance(r, MPICoresResReq)]
        sorted_mpi = sorted(mpi, key=lambda x: x[1], reverse=True)
        sorted_mpi_instances = [x[0] for x in sorted_mpi]

        return sorted_threaded_instances + sorted_mpi_instances

    def _conflicting_names(
            self, model: ModelGraph, exclusive: Set[Reference],
            component: Component, instance: Reference) -> Set[Reference]:
        """Find conflicting components.

        This returns the names of instances that cannot share resources
        with the given component, so that they can be avoided when
        assigning resources.

        Args:
            model: Model to search
            exclusive: List of instances that cannot share resources
            component: Component to find conflicts for
            instance: Instance (of component) to find conflicts for
        """
        def indices_match(
                instance1: Reference, instance2: Reference, dims: int) -> bool:
            idx1 = instance_indices(instance1)
            idx2 = instance_indices(instance2)
            return idx1[:dims] == idx2[:dims]

        def matching_instances(
                others: Set[Tuple[Component, int]]) -> Set[Reference]:
            return {
                    i for c, d in others for i in c.instances()
                    if indices_match(i, instance, d)}

        conflicting_instances = {
                i for c in model.components() for i in c.instances()}

        if instance in exclusive:
            return conflicting_instances

        conflicting_instances -= matching_instances(model.predecessors(component))
        conflicting_instances -= matching_instances(model.successors(component))

        if component not in exclusive:
            micros = matching_instances(model.micros(component))
            macros = matching_instances(model.macros(component))
            nonconflicting_mms = (micros | macros) - exclusive
            conflicting_instances -= nonconflicting_mms

        return conflicting_instances

    def _expand_resources(
            self, name: Reference, req: ResourceRequirements) -> None:
        """Adds an extra virtual node to the available resources."""
        taken = True
        while taken:
            new_node = 'node{:06d}'.format(self._next_virtual_node)
            taken = new_node in self._all_resources.cores
            self._next_virtual_node += 1

        num_cores = len(next(iter(self._all_resources.cores.values())))
        if isinstance(req, ThreadedResReq):
            if req.threads > num_cores:
                raise InsufficientResourcesAvailable(
                        f'Instance {name} requires {req.threads} threads,'
                        f' which is impossible with {num_cores} cores per'
                        ' node.')
        if isinstance(req, MPICoresResReq):
            if req.threads_per_mpi_process > num_cores:
                raise InsufficientResourcesAvailable(
                        f'Instance {name} requires'
                        f' {req.threads_per_mpi_process} threads per process,'
                        f' which is impossible with {num_cores} cores per'
                        ' node.')
        self._all_resources.cores[new_node] = set(range(num_cores))

    def _allocate_instance(
            self, instance: Reference, component: Component,
            requirements: ResourceRequirements,
            simultaneous_instances: Set[Reference], virtual: bool
            ) -> Resources:
        """Allocates resources for the given instance.

        If we are on real resources, and the instance requires more
        threads than our nodes have cores, then we'll just give it all
        cores on a node and hope for the best. If we are on virtual
        resources, this will raise InsufficientResourcesAvailable.

        Args:
            instance: The instance to allocate for
            component: The component it is an instance of
            requirements: Its resource requirements
            simultaneous_instances: Instances which may execute
                    simultaneously and whose resources we therefore
                    cannot overlap with
            virtual: Whether we are on virtual resources

        Returns:
            A Resources object describing the resources allocated
        """
        allocation = Resources({})
        free_resources = copy(self._all_resources)

        for other in self._allocations:
            if other in simultaneous_instances:
                free_resources -= self._allocations[other]

        try:
            if isinstance(requirements, ThreadedResReq):
                allocation = self._allocate_thread_block(
                        free_resources, requirements.threads)

            elif isinstance(requirements, MPICoresResReq):
                if requirements.threads_per_mpi_process != 1:
                    raise RuntimeError(
                            'Multiple threads per MPI process is not supported'
                            ' yet. Please make an issue on GitHub.')
                for proc in range(requirements.mpi_processes):
                    allocation += self._allocate_thread_block(
                            free_resources,
                            requirements.threads_per_mpi_process)
                    free_resources -= allocation

            elif isinstance(requirements, MPINodesResReq):
                raise RuntimeError(
                        'Node-based MPI resource requirements are not'
                        ' supported yet. Please make an issue on GitHub.')

        except InsufficientResourcesAvailable:
            if not self._allocations and not virtual:
                # There are no other allocations and it's still not
                # enough. Just give it all and hope for the best.
                _logger.warning((
                        'Instance {} requires more resources than are'
                        ' available in total. Oversubscribing this'
                        ' instance.').format(instance))
                allocation = copy(self._all_resources)
            else:
                raise

        self._allocations[instance] = allocation
        return allocation

    def _allocate_thread_block(
            self, free_resources: Resources, threads: int) -> Resources:
        """Allocate resources for a group of threads.

        This chooses a set of <threads> cores on the same node. It
        returns the allocated resources; it doesn't update
        self._allocations or free_resources.

        Args:
            threads: Number of cores
            free_resources: Available resources to allocate from

        Returns:
            The allocated resources
        """
        for node in free_resources.nodes():
            if len(free_resources.cores[node]) >= threads:
                available_cores = sorted(free_resources.cores[node])
                to_reserve = set(available_cores[:threads])
                return Resources({node: to_reserve})
        raise InsufficientResourcesAvailable()
