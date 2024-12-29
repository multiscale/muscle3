import pytest
from typing import Dict, List

from ymmsl import (
        Component, Conduit, Configuration, Implementation, Model,
        MPICoresResReq, Ports, Reference, ResourceRequirements, ThreadedResReq)

from libmuscle.planner.planner import (
        InsufficientResourcesAvailable, ModelGraph, Planner, ResourceAssignment)
from libmuscle.planner.resources import Resources

from libmuscle.test.conftest import core as c, on_node_resources as onr, resources


Ref = Reference


@pytest.fixture
def all_resources() -> Resources:
    return resources({
        'node001': [c(1), c(2), c(3), c(4)],
        'node002': [c(1), c(2), c(3), c(4)],
        'node003': [c(1), c(2), c(3), c(4)]})


@pytest.fixture
def init() -> Component:
    return Component('init', 'init', ports=Ports(o_f=['state_out']))


@pytest.fixture
def macro() -> Component:
    return Component('macro', 'macro', ports=Ports(
            f_init=['initial_state_in'], o_i=['bc_out'], s=['bc_in']))


@pytest.fixture
def micro() -> Component:
    return Component('micro', 'micro', ports=Ports(
            f_init=['initial_bc_in'], o_f=['final_bc_out']))


@pytest.fixture
def model(init: Component, macro: Component, micro: Component) -> Model:
    return Model(
            'test_model',
            [init, macro, micro],
            [
                Conduit('init.state_out', 'macro.initial_state_in'),
                Conduit('macro.bc_out', 'micro.initial_bc_in'),
                Conduit('micro.final_bc_out', 'macro.bc_in')])


@pytest.fixture
def implementations() -> List[Implementation]:
    return [
            Implementation(Ref('init'), script='init'),
            Implementation(Ref('macro'), script='macro'),
            Implementation(Ref('micro'), script='micro')]


@pytest.fixture
def requirements() -> Dict[Reference, ResourceRequirements]:
    res_list = [
            ThreadedResReq(Ref('init'), 4),
            ThreadedResReq(Ref('macro'), 4),
            ThreadedResReq(Ref('micro'), 4)]
    return {r.name: r for r in res_list}


@pytest.fixture
def configuration(
        model: Model, implementations: List[Implementation],
        requirements: Dict[Reference, ResourceRequirements]) -> Configuration:
    return Configuration(model, None, implementations, requirements)


@pytest.fixture
def assignment() -> ResourceAssignment:
    return ResourceAssignment([
        onr('node001', {0, 1}),
        onr('node002', {2, 3})])


def test_model_graph(
        init: Component, macro: Component, micro: Component, model: Model
        ) -> None:
    graph = ModelGraph(model)

    assert graph.components() == model.components

    assert not graph.predecessors(init)
    assert not graph.macros(init)
    assert not graph.micros(init)
    assert graph.successors(init) == {(macro, 0), (micro, 0)}

    assert graph.predecessors(macro) == {(init, 0)}
    assert not graph.macros(macro)
    assert graph.micros(macro) == {(micro, 0)}
    assert not graph.successors(macro)

    assert graph.predecessors(micro) == {(init, 0)}
    assert graph.macros(micro) == {(macro, 0)}
    assert not graph.micros(micro)
    assert not graph.successors(micro)


def test_resource_assignment_eq() -> None:
    asm1 = ResourceAssignment([])
    asm2 = ResourceAssignment([])

    assert asm1 == asm2

    asm1.by_rank.append(onr('node001', {0, 1}))
    assert asm1 != asm2

    asm2.by_rank.append(onr('node001', {0, 2}))
    assert asm1 != asm2

    asm2.by_rank[0] = onr('node001', {0, 1})
    assert asm1 == asm2


def test_resource_assignment_str(assignment: ResourceAssignment) -> None:
    assert str(assignment) == (
            '[OnNodeResources(node001, c: 0-1(0-1)),'
            ' OnNodeResources(node002, c: 2-3(2-3))]')


def test_resource_assignment_repr(assignment: ResourceAssignment) -> None:
    assert repr(assignment) == (
            'ResourceAssignment(['
            'OnNodeResources("node001", CoreSet({Core(0, {0}), Core(1, {1})})),'
            ' OnNodeResources("node002", CoreSet({Core(2, {2}), Core(3, {3})}))])')


def test_resource_assignment_as_resources(assignment) -> None:
    res = assignment.as_resources()

    assert res._nodes == {
            'node001': onr('node001', {0, 1}),
            'node002': onr('node002', {2, 3})}

    asm2 = ResourceAssignment([
        onr('node001', {0, 1}), onr('node001', {2, 3}), onr('node001', {2, 3}),
        onr('node003', {4, 5})])

    res = asm2.as_resources()

    assert res._nodes == {
            'node001': onr('node001', {0, 1, 2, 3}),
            'node003': onr('node003', {4, 5})}


def test_planner(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('micro')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_planner_exclusive_macro(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    configuration.implementations[Ref('macro')].can_share_resources = False
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro')].by_rank == [onr('node002', {1, 2, 3, 4})]
    assert allocations[Ref('micro')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_planner_exclusive_predecessor(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    configuration.implementations[Ref('init')].can_share_resources = False
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('micro')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_oversubscribe(
        all_resources: Resources, configuration: Configuration) -> None:

    for i in range(3):
        configuration.model.components[i].multiplicity = [5]

    planner = Planner(all_resources)
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init[0]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('init[1]')].by_rank == [onr('node002', {1, 2, 3, 4})]
    assert allocations[Ref('init[2]')].by_rank == [onr('node003', {1, 2, 3, 4})]
    assert allocations[Ref('init[3]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('init[4]')].by_rank == [onr('node002', {1, 2, 3, 4})]

    assert allocations[Ref('macro[0]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro[1]')].by_rank == [onr('node002', {1, 2, 3, 4})]
    assert allocations[Ref('macro[2]')].by_rank == [onr('node003', {1, 2, 3, 4})]
    assert allocations[Ref('macro[3]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro[4]')].by_rank == [onr('node002', {1, 2, 3, 4})]

    assert allocations[Ref('micro[0]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('micro[1]')].by_rank == [onr('node002', {1, 2, 3, 4})]
    assert allocations[Ref('micro[2]')].by_rank == [onr('node003', {1, 2, 3, 4})]
    assert allocations[Ref('micro[3]')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('micro[4]')].by_rank == [onr('node002', {1, 2, 3, 4})]


def test_oversubscribe_single_instance_threaded() -> None:
    model = Model('single_instance', [Component('x', 'x', ports=Ports())])
    impl = [Implementation(Ref('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Ref('x'): ThreadedResReq(Ref('x'), 24)}
    config = Configuration(model, None, impl, reqs)

    res = resources({'node001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert allocations[Ref('x')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_oversubscribe_single_instance_mpi() -> None:
    model = Model('single_instance', [Component('x', 'x', ports=Ports())])
    impl = [Implementation(Ref('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Ref('x'): MPICoresResReq(Ref('x'), 24)}
    config = Configuration(model, None, impl, reqs)

    res = resources({'node001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert len(allocations[Ref('x')].by_rank) == 24
    for r in range(24):
        assert allocations[Ref('x')].by_rank[r] == onr('node001', {r % 4 + 1})


def test_virtual_allocation() -> None:
    model = Model('ensemble', [Component('x', 'x', 9, ports=Ports())])
    impl = [Implementation(Ref('x'), script='x')]
    reqs: Dict[Ref, ResourceRequirements] = {
            Ref('x'): MPICoresResReq(Ref('x'), 13)}
    config = Configuration(model, None, impl, reqs)

    res = resources({'node000001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config, virtual=True)

    assert res.total_cores() == 120
    for i in range(9):
        for r in range(13):
            assert len(allocations[Ref(f'x[{i}]')].by_rank) == 13
            assert allocations[Ref(f'x[{i}]')].by_rank[r].total_cores() == 1


def test_impossible_virtual_allocation() -> None:
    model = Model('ensemble', [Component('x', 'x', 9, ports=Ports())])
    impl = [Implementation(Ref('x'), script='x')]
    reqs: Dict[Ref, ResourceRequirements] = {
            Ref('x'): ThreadedResReq(Ref('x'), 13)}
    config = Configuration(model, None, impl, reqs)

    res = resources({'node000001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    with pytest.raises(InsufficientResourcesAvailable):
        planner.allocate_all(config, virtual=True)
