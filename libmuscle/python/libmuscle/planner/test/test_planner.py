import pytest
from libmuscle.planner.planner import (
    InsufficientResourcesAvailable,
    ModelGraph,
    Planner,
    ResourceAssignment,
)
from libmuscle.planner.resources import Resources
from libmuscle.test.conftest import core as c
from libmuscle.test.conftest import on_node_resources as onr
from libmuscle.test.conftest import resources
from ymmsl.v0_2 import (
    Component,
    Conduit,
    Configuration,
    Model,
    MPICoresResReq,
    Ports,
    Program,
    Reference,
    ResourceRequirements,
    ThreadedResReq,
)

Ref = Reference


@pytest.fixture
def all_resources() -> Resources:
    return resources({
        'node001': [c(1), c(2), c(3), c(4)],
        'node002': [c(1), c(2), c(3), c(4)],
        'node003': [c(1), c(2), c(3), c(4)]})


@pytest.fixture
def init() -> Component:
    return Component('init', Ports(o_f=['state_out']), '', 'init')


@pytest.fixture
def macro() -> Component:
    return Component(
            'macro', Ports(f_init=['initial_state_in'], o_i=['bc_out'], s=['bc_in']),
            '', 'macro')


@pytest.fixture
def micro() -> Component:
    return Component(
            'micro', Ports(f_init=['initial_bc_in'], o_f=['final_bc_out']), '', 'micro')


@pytest.fixture
def model(init: Component, macro: Component, micro: Component) -> Model:
    return Model(
            'test_model', None, '', None, [init, macro, micro],
            [
                Conduit('init.state_out', 'macro.initial_state_in'),
                Conduit('macro.bc_out', 'micro.initial_bc_in'),
                Conduit('micro.final_bc_out', 'macro.bc_in')])


@pytest.fixture
def programs() -> list[Program]:
    return [
            Program(Ref('init'), script='init'),
            Program(Ref('macro'), script='macro'),
            Program(Ref('micro'), script='micro')]


@pytest.fixture
def requirements() -> dict[Reference, ResourceRequirements]:
    res_list = [
            ThreadedResReq(Ref('test_model.init'), 4),
            ThreadedResReq(Ref('test_model.macro'), 4),
            ThreadedResReq(Ref('test_model.micro'), 4)]
    return {r.name: r for r in res_list}


@pytest.fixture
def configuration(
        model: Model, programs: list[Program],
        requirements: dict[Reference, ResourceRequirements]) -> Configuration:
    return Configuration('config', [], [model], None, None, programs, requirements)


@pytest.fixture
def assignment() -> ResourceAssignment:
    return ResourceAssignment([
        onr('node001', {0, 1}),
        onr('node002', {2, 3})])


def test_model_graph(
        init: Component, macro: Component, micro: Component, model: Model
        ) -> None:
    graph = ModelGraph(model)

    assert set(graph.components()) == set(model.components.values())

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
    configuration.programs[Ref('macro')].can_share_resources = False
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro')].by_rank == [onr('node002', {1, 2, 3, 4})]
    assert allocations[Ref('micro')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_planner_exclusive_predecessor(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    configuration.programs[Ref('init')].can_share_resources = False
    allocations = planner.allocate_all(configuration)

    assert allocations[Ref('init')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('macro')].by_rank == [onr('node001', {1, 2, 3, 4})]
    assert allocations[Ref('micro')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_oversubscribe(
        all_resources: Resources, configuration: Configuration) -> None:

    for component in configuration.models['test_model'].components.values():
        component.multiplicity = [5]

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
    model = Model('single_instance', None, '', None, [Component('x', Ports(), '', 'x')])
    programs = [Program(Ref('x'), script='x')]
    reqs: dict[Reference, ResourceRequirements] = {
            Ref('single_instance.x'): ThreadedResReq(Ref('single_instance.x'), 24)}
    config = Configuration('config', [], [model], None, None, programs, reqs)

    res = resources({'node001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert allocations[Ref('x')].by_rank == [onr('node001', {1, 2, 3, 4})]


def test_oversubscribe_single_instance_mpi() -> None:
    model = Model('single_instance', None, '', None, [Component('x', Ports(), '', 'x')])
    programs = [Program(Ref('x'), script='x')]
    reqs: dict[Reference, ResourceRequirements] = {
            Ref('single_instance.x'): MPICoresResReq(Ref('single_instance.x'), 24)}
    config = Configuration('config', [], [model], None, None, programs, reqs)

    res = resources({'node001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert len(allocations[Ref('x')].by_rank) == 24
    for r in range(24):
        assert allocations[Ref('x')].by_rank[r] == onr('node001', {r % 4 + 1})


def test_virtual_allocation() -> None:
    model = Model(
            'ensemble', None, '', None, [Component('x', Ports(), '', 'x', False, 9)])
    programs = [Program(Ref('x'), script='x')]
    reqs: dict[Ref, ResourceRequirements] = {
            Ref('ensemble.x'): MPICoresResReq(Ref('ensemble.x'), 13)}
    config = Configuration('config', [], [model], None, None, programs, reqs)

    res = resources({'node000001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    allocations = planner.allocate_all(config, virtual=True)

    assert res.total_cores() == 120
    for i in range(9):
        for r in range(13):
            assert len(allocations[Ref(f'x[{i}]')].by_rank) == 13
            assert allocations[Ref(f'x[{i}]')].by_rank[r].total_cores() == 1


def test_impossible_virtual_allocation() -> None:
    model = Model(
            'ensemble', None, '', None, [Component('x', Ports(), '', 'x', False, 9)])
    program = [Program(Ref('x'), script='x')]
    reqs: dict[Ref, ResourceRequirements] = {
            Ref('ensemble.x'): ThreadedResReq(Ref('ensemble.x'), 13)}
    config = Configuration('config', [], [model], None, None, program, reqs)

    res = resources({'node000001': [c(1), c(2), c(3), c(4)]})

    planner = Planner(res)
    with pytest.raises(InsufficientResourcesAvailable):
        planner.allocate_all(config, virtual=True)
