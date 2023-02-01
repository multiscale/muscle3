from libmuscle.planner.planner import (
        InsufficientResourcesAvailable, ModelGraph, Planner, Resources)

from copy import copy
import pytest
from typing import Dict, List

from ymmsl import (
        Component, Conduit, Configuration, Implementation, Model,
        MPICoresResReq, Ports, Reference, ResourceRequirements, ThreadedResReq)


@pytest.fixture
def all_resources() -> Resources:
    return Resources({
        'node001': {1, 2, 3, 4},
        'node002': {1, 2, 3, 4},
        'node003': {1, 2, 3, 4}})


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
            Implementation(Reference('init'), script='init'),
            Implementation(Reference('macro'), script='macro'),
            Implementation(Reference('micro'), script='micro')]


@pytest.fixture
def requirements() -> Dict[Reference, ResourceRequirements]:
    res_list = [
            ThreadedResReq(Reference('init'), 4),
            ThreadedResReq(Reference('macro'), 4),
            ThreadedResReq(Reference('micro'), 4)]
    return {r.name: r for r in res_list}


@pytest.fixture
def configuration(
        model: Model, implementations: List[Implementation],
        requirements: Dict[Reference, ResourceRequirements]) -> Configuration:
    return Configuration(model, None, implementations, requirements)


def test_model_graph(
        init: Component, macro: Component, micro: Component, model: Model
        ) -> None:
    graph = ModelGraph(model)

    assert graph.components() == model.components

    assert not graph.predecessors(init)
    assert not graph.macros(init)
    assert not graph.micros(init)
    assert graph.successors(init) == {macro, micro}

    assert graph.predecessors(macro) == {init}
    assert not graph.macros(macro)
    assert graph.micros(macro) == {micro}
    assert not graph.successors(macro)

    assert graph.predecessors(micro) == {init}
    assert graph.macros(micro) == {macro}
    assert not graph.micros(micro)
    assert not graph.successors(micro)


def test_resources(all_resources: Resources) -> None:
    res1 = all_resources
    assert res1.cores == {
            'node001': {1, 2, 3, 4},
            'node002': {1, 2, 3, 4},
            'node003': {1, 2, 3, 4}}
    assert set(res1.nodes()) == {'node001', 'node002', 'node003'}

    res2 = Resources({
        'node004': {1, 2, 3, 4, 5, 6}, 'node005': {1, 2, 3, 4, 5, 6}})
    res1 += res2

    assert res1.cores == {
            'node001': {1, 2, 3, 4}, 'node002': {1, 2, 3, 4},
            'node003': {1, 2, 3, 4}, 'node004': {1, 2, 3, 4, 5, 6},
            'node005': {1, 2, 3, 4, 5, 6}}

    res3 = Resources({'node003': {1, 2, 3, 4}, 'node005': {4, 5, 6}})
    res1 -= res3

    assert res1.cores == {
            'node001': {1, 2, 3, 4}, 'node002': {1, 2, 3, 4},
            'node004': {1, 2, 3, 4, 5, 6}, 'node005': {1, 2, 3}}
    assert res1.nodes() == {
            'node001', 'node002', 'node004', 'node005'}

    res4 = copy(res3)
    res4.cores['node003'] = {8}

    assert res3.cores['node003'] == {1, 2, 3, 4}
    assert res4.cores['node003'] == {8}

    all_resources = Resources.union([res1, res2, res3, res4])

    assert all_resources.cores['node001'] == {1, 2, 3, 4}
    assert all_resources.cores['node002'] == {1, 2, 3, 4}
    assert all_resources.cores['node003'] == {1, 2, 3, 4, 8}
    assert all_resources.cores['node004'] == {1, 2, 3, 4, 5, 6}
    assert all_resources.cores['node005'] == {1, 2, 3, 4, 5, 6}


def test_planner(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    allocations = planner.allocate_all(configuration)

    assert allocations[Reference('init')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('macro')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('micro')].cores == {'node001': {1, 2, 3, 4}}


def test_planner_exclusive_macro(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    configuration.implementations[Reference('macro')].can_share_resources = (
            False)
    allocations = planner.allocate_all(configuration)

    assert allocations[Reference('init')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('macro')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('micro')].cores == {'node002': {1, 2, 3, 4}}


def test_planner_exclusive_predecessor(
        all_resources: Resources, configuration: Configuration) -> None:
    planner = Planner(all_resources)
    configuration.implementations[Reference('init')].can_share_resources = (
            False)
    allocations = planner.allocate_all(configuration)

    assert allocations[Reference('init')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('macro')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('micro')].cores == {'node001': {1, 2, 3, 4}}


def test_oversubscribe(
        all_resources: Resources, configuration: Configuration) -> None:

    for i in range(3):
        configuration.model.components[i].multiplicity = [5]

    planner = Planner(all_resources)
    allocations = planner.allocate_all(configuration)

    assert allocations[Reference('init[0]')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('init[1]')].cores == {'node002': {1, 2, 3, 4}}
    assert allocations[Reference('init[2]')].cores == {'node003': {1, 2, 3, 4}}
    assert allocations[Reference('init[3]')].cores == {'node001': {1, 2, 3, 4}}
    assert allocations[Reference('init[4]')].cores == {'node002': {1, 2, 3, 4}}

    assert allocations[Reference('macro[0]')].cores == {
            'node001': {1, 2, 3, 4}}
    assert allocations[Reference('macro[1]')].cores == {
            'node002': {1, 2, 3, 4}}
    assert allocations[Reference('macro[2]')].cores == {
            'node003': {1, 2, 3, 4}}
    assert allocations[Reference('macro[3]')].cores == {
            'node001': {1, 2, 3, 4}}
    assert allocations[Reference('macro[4]')].cores == {
            'node002': {1, 2, 3, 4}}

    assert allocations[Reference('micro[0]')].cores == {
            'node001': {1, 2, 3, 4}}
    assert allocations[Reference('micro[1]')].cores == {
            'node002': {1, 2, 3, 4}}
    assert allocations[Reference('micro[2]')].cores == {
            'node003': {1, 2, 3, 4}}
    assert allocations[Reference('micro[3]')].cores == {
            'node001': {1, 2, 3, 4}}
    assert allocations[Reference('micro[4]')].cores == {
            'node002': {1, 2, 3, 4}}


def test_oversubscribe_single_instance_threaded() -> None:
    model = Model('single_instance', [Component('x', 'x', ports=Ports())])
    impl = [Implementation(Reference('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Reference('x'): ThreadedResReq(Reference('x'), 24)}
    config = Configuration(model, None, impl, reqs)

    res = Resources({'node001': {1, 2, 3, 4}})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert allocations[Reference('x')].cores == {'node001': {1, 2, 3, 4}}


def test_oversubscribe_single_instance_mpi() -> None:
    model = Model('single_instance', [Component('x', 'x', ports=Ports())])
    impl = [Implementation(Reference('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Reference('x'): MPICoresResReq(Reference('x'), 24)}
    config = Configuration(model, None, impl, reqs)

    res = Resources({'node001': {1, 2, 3, 4}})

    planner = Planner(res)
    allocations = planner.allocate_all(config)

    assert allocations[Reference('x')].cores == {'node001': {1, 2, 3, 4}}


def test_virtual_allocation() -> None:
    model = Model('ensemble', [Component('x', 'x', 9, ports=Ports())])
    impl = [Implementation(Reference('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Reference('x'): MPICoresResReq(Reference('x'), 13)}
    config = Configuration(model, None, impl, reqs)

    res = Resources({'node000001': {1, 2, 3, 4}})

    planner = Planner(res)
    allocations = planner.allocate_all(config, virtual=True)

    assert res.total_cores() == 120
    assert allocations[Reference('x[0]')].total_cores() == 13
    assert allocations[Reference('x[8]')].total_cores() == 13


def test_impossible_virtual_allocation() -> None:
    model = Model('ensemble', [Component('x', 'x', 9, ports=Ports())])
    impl = [Implementation(Reference('x'), script='x')]
    reqs: Dict[Reference, ResourceRequirements] = {
            Reference('x'): ThreadedResReq(Reference('x'), 13)}
    config = Configuration(model, None, impl, reqs)

    res = Resources({'node000001': {1, 2, 3, 4}})

    planner = Planner(res)
    with pytest.raises(InsufficientResourcesAvailable):
        planner.allocate_all(config, virtual=True)
