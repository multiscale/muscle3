from libmuscle.planner.planner import ModelGraph, Planner, Resources

from typing import Dict, Set, Tuple

import pytest
from ymmsl import (
        Component, Conduit, Model, MPICoresResReq, Ports, Reference,
        ResourceRequirements, ThreadedResReq)


_ResReqs = Dict[Reference, ResourceRequirements]


_Scenario = Tuple[Model, _ResReqs, Resources, Set[Component]]


s0_model = Model(
        'semidetached_macro_micro',
        [
            Component('macro', ports=Ports(o_i=['out'])),
            Component('micro', ports=Ports(f_init=['in']))],
        [
            Conduit('macro.out', 'micro.in')])


s0_requirements = {
        'macro': ThreadedResReq(Reference('macro'), 2),
        'micro': ThreadedResReq(Reference('micro'), 2)}


s0_resources = Resources({'node001': {0, 1, 2, 3}})


s1_model = Model(
        'serial_micros',
        [
            Component('macro', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro3', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'micro3.bc_in'),
            Conduit('micro3.bc_out', 'macro.bc_in')])


s1_res_list = [
        ThreadedResReq(Reference('macro'), 4),
        ThreadedResReq(Reference('micro1'), 2),
        ThreadedResReq(Reference('micro2'), 2),
        ThreadedResReq(Reference('micro3'), 1)]


s1_requirements = {r.name: r for r in s1_res_list}


s1_resources = Resources({'node001': {0, 1, 2, 3}})


s2_model = Model(
        'parallel_micros',
        [
            Component('macro', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('macro.bc_out', 'micro2.bc_in'),
            Conduit('micro1.bc_out', 'macro.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s2_res_list = [
        ThreadedResReq(Reference('macro'), 1),
        ThreadedResReq(Reference('micro1'), 3),
        ThreadedResReq(Reference('micro2'), 2)]


s2_requirements = {r.name: r for r in s2_res_list}


s2_resources = Resources({'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3}})


s3_model = Model(
        'diamond',
        [
            Component('a', ports=Ports(o_f=['out'])),
            Component('b1', ports=Ports(
                f_init=['in'], o_f=['out'])),
            Component('b2', ports=Ports(
                f_init=['in'], o_f=['out'])),
            Component('c', ports=Ports(
                f_init=['in'], o_f=['bc_out']))],
        [
            Conduit('a.out', 'b1.in'),
            Conduit('a.out', 'b2.in'),
            Conduit('b1.out', 'c.in'),
            Conduit('b2.out', 'c.in')])


s3_res_list = [
        ThreadedResReq(Reference('a'), 1),
        MPICoresResReq(Reference('b1'), 6),
        ThreadedResReq(Reference('b2'), 2),
        ThreadedResReq(Reference('c'), 4)]


s3_requirements = {r.name: r for r in s3_res_list}


s3_resources = Resources({'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3}})


s4_model = Model(
        'lockstep_macros_micro',
        [
            Component('macro1', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('macro2', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('micro', ports=Ports(
                f_init=['bc_in1', 'bc_in2'], o_f=['bc_out1', 'bc_out2']))],
        [
            Conduit('macro1.bc_out', 'micro.bc_in1'),
            Conduit('macro2.bc_out', 'micro.bc_in2'),
            Conduit('micro.bc_out1', 'macro1.bc_in'),
            Conduit('micro.bc_out1', 'macro2.bc_in')])


s4_res_list = [
        ThreadedResReq(Reference('macro1'), 2),
        ThreadedResReq(Reference('macro2'), 3),
        ThreadedResReq(Reference('micro'), 3)]


s4_requirements = {r.name: r for r in s4_res_list}


s4_resources = Resources({'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3}})


s5_model = Model(
        'repeater',
        [
            Component('init', ports=Ports(o_f=['out1', 'out2'])),
            Component('macro', ports=Ports(
                f_init=['in'], o_i=['bc_out'], s=['bc_in'])),
            Component('micro', ports=Ports(
                f_init=['in', 'in2'], o_f=['out'])),
            Component('repeater', ports=Ports(
                f_init=['data_in'], o_i=['data_out', 'trigger_out'],
                s=['trigger_in']))],
        [
            Conduit('init.out1', 'macro.in'),
            Conduit('init.out2', 'repeater.data_in'),
            Conduit('macro.bc_out', 'repeater.trigger_in'),
            Conduit('repeater.trigger_out', 'micro.in'),
            Conduit('repeater.data_out', 'micro.in2'),
            Conduit('micro.out', 'macro.bc_in')])


s5_res_list = [
        ThreadedResReq(Reference('init'), 4),
        MPICoresResReq(Reference('repeater'), 1),
        ThreadedResReq(Reference('macro'), 4),
        ThreadedResReq(Reference('micro'), 4)]


s5_requirements = {r.name: r for r in s5_res_list}


s5_resources = Resources({
    'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3}, 'node003': {0, 1}})


s6_model = Model(
        'scale_overlap',
        [
            Component('a', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('tcf', ports=Ports(
                o_i=['a_out', 'b_out'], s=['a_in', 'b_in'])),
            Component('b', ports=Ports(
                o_i=['bc_out'], s=['bc_in']))],
        [
            Conduit('a.bc_out', 'tcf.a_in'),
            Conduit('tcf.a_out', 'a.bc_in'),
            Conduit('b.bc_out', 'tcf.b_in'),
            Conduit('tcf.b_out', 'b.bc_in')])


s6_res_list = [
        ThreadedResReq(Reference('a'), 4),
        MPICoresResReq(Reference('b'), 16),
        ThreadedResReq(Reference('tcf'), 1)]


s6_requirements = {r.name: r for r in s6_res_list}


s6_resources = Resources({
        'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3},
        'node003': {0, 1, 2, 3}, 'node004': {0, 1, 2, 3},
        'node005': {0, 1, 2, 3}, 'node006': {0, 1, 2, 3}
        })


s7_model = Model(
        'monte_carlo_init_macro_micro',
        [
            Component('mc', ports=Ports(
                o_i=['pars_out'], s=['results_in'])),
            Component('init', None, 10, Ports(o_f=['state_out'])),
            Component('macro', None, 10, Ports(
                f_init=['state_in'], o_i=['bc_out'], s=['bc_in'],
                o_f=['final_out'])),
            Component('micro', None, 10, Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('mc.pars_out', 'init.muscle_settings_in'),
            Conduit('init.state_out', 'macro.state_in'),
            Conduit('macro.bc_out', 'micro.bc_in'),
            Conduit('micro.bc_out', 'macro.bc_in'),
            Conduit('macro.final_out', 'mc.results_in')])


s7_res_list = [
        ThreadedResReq(Reference('mc'), 1),
        ThreadedResReq(Reference('init'), 4),
        ThreadedResReq(Reference('macro'), 4),
        MPICoresResReq(Reference('micro'), 4)]


s7_requirements = {r.name: r for r in s7_res_list}


s7_resources = Resources({
        'node001': {0, 1, 2, 3, 4, 5, 6, 7},
        'node002': {0, 1, 2, 3, 4, 5, 6, 7},
        'node003': {0, 1, 2, 3, 4, 5, 6, 7},
        'node004': {0, 1, 2, 3, 4, 5, 6, 7},
        'node005': {0, 1, 2, 3, 4, 5, 6, 7},
        })


s8_model = Model(
        'serial_micros_exclusive_macro',
        [
            Component('macro', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s8_res_list = [
        ThreadedResReq(Reference('macro'), 1),
        ThreadedResReq(Reference('micro1'), 3),
        ThreadedResReq(Reference('micro2'), 2)]


s8_requirements = {r.name: r for r in s8_res_list}


s8_resources = Resources({'node001': {0, 1, 2, 3}, 'node002': {0, 1, 2, 3}})


s8_exclusive = {s8_model.components[0]}


s9_model = Model(
        'converging_graph',
        [
            Component('e', ports=Ports(o_f=['out'])),
            Component('b', ports=Ports(
                f_init=['in'], o_f=['out'])),
            Component('c', ports=Ports(f_init=['in'])),
            Component('a', ports=Ports(o_f=['out'])),
            Component('d', ports=Ports(
                f_init=['in'], o_f=['out'])),
            ],
        [
            Conduit('e.out', 'b.in'),
            Conduit('b.out', 'c.in'),
            Conduit('a.out', 'd.in'),
            Conduit('d.out', 'b.in')])


s9_res_list = [
        ThreadedResReq(Reference('a'), 1),
        ThreadedResReq(Reference('b'), 1),
        ThreadedResReq(Reference('c'), 1),
        ThreadedResReq(Reference('d'), 1),
        ThreadedResReq(Reference('e'), 1)]


s9_requirements = {r.name: r for r in s9_res_list}


s9_resources = Resources({'node001': {0, 1, 2, 3}})


scenarios = [
        (s0_model, s0_requirements, s0_resources, set()),
        (s1_model, s1_requirements, s1_resources, set()),
        (s2_model, s2_requirements, s2_resources, set()),
        (s3_model, s3_requirements, s3_resources, set()),
        (s4_model, s4_requirements, s4_resources, set()),
        (s5_model, s5_requirements, s5_resources, set()),
        (s6_model, s6_requirements, s6_resources, set()),
        (s7_model, s7_requirements, s7_resources, set()),
        (s8_model, s8_requirements, s8_resources, s8_exclusive),
        (s9_model, s9_requirements, s9_resources, set()),
        ]


@pytest.mark.parametrize('scenario', scenarios)
def test_scenarios(scenario: _Scenario) -> None:
    model, reqs, res, excl = scenario
    planner = Planner(res)
    model_graph = ModelGraph(model)
    allocations = planner.allocate_all(model_graph, reqs, excl)

    for cname, req in reqs.items():
        # check that we have enough cores
        component = [
            c for c in model_graph.components()
            if c.name == cname][0]

        if isinstance(req, ThreadedResReq):
            for instance in component.instances():
                assert len(list(allocations[instance].nodes())) == 1
                assert allocations[instance].total_cores() == req.threads
        elif isinstance(req, MPICoresResReq):
            for instance in component.instances():
                tcores = allocations[instance].total_cores()
                assert tcores == req.mpi_processes

    # check for any overlapping instances
    for instance1, res1 in allocations.items():
        for instance2, res2 in allocations.items():
            cname1 = instance1.without_trailing_ints()
            cname2 = instance2.without_trailing_ints()
            if cname1 != cname2:
                if not res1.isdisjoint(res2):
                    comp1 = [
                        c for c in model_graph.components()
                        if c.name == cname1][0]
                    comp2 = [
                        c for c in model_graph.components()
                        if c.name == cname2][0]
                    assert (
                            comp2 in model_graph.successors(comp1) or
                            comp2 in model_graph.predecessors(comp1) or
                            (
                                comp2 in model_graph.macros(comp1) and
                                comp2 not in excl and comp1 not in excl) or
                            (
                                comp2 in model_graph.micros(comp1) and
                                comp2 not in excl and comp1 not in excl))

            elif instance1 != instance2:
                assert res1.isdisjoint(res2)
