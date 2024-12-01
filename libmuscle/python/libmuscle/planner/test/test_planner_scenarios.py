from copy import deepcopy
from libmuscle.planner.planner import ModelGraph, Planner, Resources

from typing import Dict, FrozenSet, Tuple

import pytest
from ymmsl import (
        Component, Conduit, Configuration, Implementation, Model,
        MPICoresResReq, Ports, Reference, ResourceRequirements, ThreadedResReq)


def c(hwthread_id: int) -> FrozenSet[int]:
    """Helper that defines a core with the given hwthread id."""
    return frozenset({hwthread_id})


_ResReqs = Dict[Reference, ResourceRequirements]


_Scenario = Tuple[Configuration, Resources]


s0_model = Model(
        'semidetached_macro_micro',
        [
            Component('macro', 'macro', ports=Ports(o_i=['out'])),
            Component('micro', 'micro', ports=Ports(f_init=['in']))],
        [
            Conduit('macro.out', 'micro.in')])


s0_implementations = [
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro'), script='micro')]


s0_requirements = [
        ThreadedResReq(Reference('macro'), 2),
        ThreadedResReq(Reference('micro'), 2)]


s0_config = Configuration(
        s0_model, None, s0_implementations, s0_requirements)


s0_resources = Resources({'node001': {c(0), c(1), c(2), c(3)}})


s0_solution = {
        Reference('macro'): Resources({'node001': {c(0), c(1)}}),
        Reference('micro'): Resources({'node001': {c(2), c(3)}})}


s1_model = Model(
        'serial_micros',
        [
            Component('macro', 'macro', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', 'micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', 'micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro3', 'micro3', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'micro3.bc_in'),
            Conduit('micro3.bc_out', 'macro.bc_in')])


s1_implementations = [
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro1'), script='micro1'),
        Implementation(Reference('micro2'), script='micro2'),
        Implementation(Reference('micro3'), script='micro3'),
        ]


s1_requirements = [
        ThreadedResReq(Reference('macro'), 4),
        ThreadedResReq(Reference('micro1'), 2),
        ThreadedResReq(Reference('micro2'), 2),
        ThreadedResReq(Reference('micro3'), 1)]


s1_config = Configuration(
        s1_model, None, s1_implementations, s1_requirements)


s1_resources = Resources({'node001': {c(0), c(1), c(2), c(3)}})


s1_solution = {
        Reference('macro'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro1'): Resources({'node001': {c(0), c(1)}}),
        Reference('micro2'): Resources({'node001': {c(0), c(1)}}),
        Reference('micro3'): Resources({'node001': {c(0)}})}


s2_model = Model(
        'parallel_micros',
        [
            Component('macro', 'macro', ports=Ports(o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', 'micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', 'micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('macro.bc_out', 'micro2.bc_in'),
            Conduit('micro1.bc_out', 'macro.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s2_implementations = [
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro1'), script='micro1'),
        Implementation(Reference('micro2'), script='micro2'),
        ]


s2_requirements = [
        ThreadedResReq(Reference('macro'), 1),
        ThreadedResReq(Reference('micro1'), 3),
        ThreadedResReq(Reference('micro2'), 2)]


s2_config = Configuration(
        s2_model, None, s2_implementations, s2_requirements)


s2_resources = Resources(
        {'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)}})


s2_solution = {
        Reference('macro'): Resources({'node001': {c(0)}}),
        Reference('micro1'): Resources({'node001': {c(0), c(1), c(2)}}),
        Reference('micro2'): Resources({'node002': {c(0), c(1)}})}


s3_model = Model(
        'diamond',
        [
            Component('a', 'a', ports=Ports(o_f=['out'])),
            Component('b1', 'b1', ports=Ports(
                f_init=['in'], o_f=['out'])),
            Component('b2', 'b2', ports=Ports(
                f_init=['in'], o_f=['out'])),
            Component('c', 'c', ports=Ports(
                f_init=['in'], o_f=['bc_out']))],
        [
            Conduit('a.out', 'b1.in'),
            Conduit('a.out', 'b2.in'),
            Conduit('b1.out', 'c.in'),
            Conduit('b2.out', 'c.in')])


s3_implementations = [
        Implementation(Reference('a'), script='a'),
        Implementation(Reference('b1'), script='b'),
        Implementation(Reference('b2'), script='b'),
        Implementation(Reference('c'), script='c'),
        ]


s3_requirements = [
        ThreadedResReq(Reference('a'), 1),
        MPICoresResReq(Reference('b1'), 6),
        ThreadedResReq(Reference('b2'), 2),
        ThreadedResReq(Reference('c'), 4)]


s3_config = Configuration(
        s3_model, None, s3_implementations, s3_requirements)


s3_resources = Resources(
        {'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)}})


s3_solution = {
        Reference('a'): Resources({'node001': {c(0)}}),
        Reference('b1'): Resources(
            {'node001': {c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('b2'): Resources({'node001': {c(0), c(1)}}),
        Reference('c'): Resources({'node001': {c(0), c(1), c(2), c(3)}})}


s4_model = Model(
        'lockstep_macros_micro',
        [
            Component('macro1', 'macro1', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('macro2', 'macro2', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('micro', 'micro', ports=Ports(
                f_init=['bc_in1', 'bc_in2'], o_f=['bc_out1', 'bc_out2']))],
        [
            Conduit('macro1.bc_out', 'micro.bc_in1'),
            Conduit('macro2.bc_out', 'micro.bc_in2'),
            Conduit('micro.bc_out1', 'macro1.bc_in'),
            Conduit('micro.bc_out1', 'macro2.bc_in')])


s4_implementations = [
        Implementation(Reference('macro1'), script='macro1'),
        Implementation(Reference('macro2'), script='macro2'),
        Implementation(Reference('micro'), script='micro'),
        ]


s4_requirements = [
        ThreadedResReq(Reference('macro1'), 2),
        ThreadedResReq(Reference('macro2'), 3),
        ThreadedResReq(Reference('micro'), 3)]


s4_config = Configuration(
        s4_model, None, s4_implementations, s4_requirements)


s4_resources = Resources(
        {'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)}})


s4_solution = {
        Reference('macro1'): Resources({'node002': {c(0), c(1)}}),
        Reference('macro2'): Resources({'node001': {c(0), c(1), c(2)}}),
        Reference('micro'): Resources({'node001': {c(0), c(1), c(2)}})}


s5_model = Model(
        'repeater',
        [
            Component('init', 'init', ports=Ports(o_f=['out1', 'out2'])),
            Component('macro', 'macro', ports=Ports(
                f_init=['in'], o_i=['bc_out'], s=['bc_in'])),
            Component('micro', 'micro', ports=Ports(
                f_init=['in', 'in2'], o_f=['out'])),
            Component('repeater', 'repeater', ports=Ports(
                f_init=['data_in'], o_i=['data_out', 'trigger_out'],
                s=['trigger_in']))],
        [
            Conduit('init.out1', 'macro.in'),
            Conduit('init.out2', 'repeater.data_in'),
            Conduit('macro.bc_out', 'repeater.trigger_in'),
            Conduit('repeater.trigger_out', 'micro.in'),
            Conduit('repeater.data_out', 'micro.in2'),
            Conduit('micro.out', 'macro.bc_in')])


s5_implementations = [
        Implementation(Reference('init'), script='init'),
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro'), script='micro'),
        Implementation(Reference('repeater'), script='repeater'),
        ]


s5_requirements = [
        ThreadedResReq(Reference('init'), 4),
        MPICoresResReq(Reference('repeater'), 1),
        ThreadedResReq(Reference('macro'), 4),
        ThreadedResReq(Reference('micro'), 4)]


s5_config = Configuration(
        s5_model, None, s5_implementations, s5_requirements)


s5_resources = Resources({
    'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)},
    'node003': {c(0), c(1)}})


# This is inefficient, as the models can all share resources. But repeater
# is funny, and the algorithm cannot deal with it yet. It does give a valid
# result with no overlap, so we'll accept that for the time being.
s5_solution = {
        Reference('init'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('repeater'): Resources({'node003': {c(0)}})}


s6_model = Model(
        'scale_overlap',
        [
            Component('a', 'a', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('tcf', 'tcf', ports=Ports(
                o_i=['a_out', 'b_out'], s=['a_in', 'b_in'])),
            Component('b', 'b', ports=Ports(
                o_i=['bc_out'], s=['bc_in']))],
        [
            Conduit('a.bc_out', 'tcf.a_in'),
            Conduit('tcf.a_out', 'a.bc_in'),
            Conduit('b.bc_out', 'tcf.b_in'),
            Conduit('tcf.b_out', 'b.bc_in')])


s6_implementations = [
        Implementation(Reference('a'), script='a'),
        Implementation(Reference('tcf'), script='tcf'),
        Implementation(Reference('b'), script='b'),
        ]


s6_requirements = [
        ThreadedResReq(Reference('a'), 4),
        MPICoresResReq(Reference('b'), 16),
        ThreadedResReq(Reference('tcf'), 1)]


s6_config = Configuration(
        s6_model, None, s6_implementations, s6_requirements)


s6_resources = Resources({
        'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)},
        'node003': {c(0), c(1), c(2), c(3)}, 'node004': {c(0), c(1), c(2), c(3)},
        'node005': {c(0), c(1), c(2), c(3)}, 'node006': {c(0), c(1), c(2), c(3)}
        })


s6_solution = {
        Reference('a'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('tcf'): Resources({'node002': {c(0)}}),
        Reference('b'): Resources({
            'node002': {c(1), c(2), c(3)},
            'node003': {c(0), c(1), c(2), c(3)},
            'node004': {c(0), c(1), c(2), c(3)},
            'node005': {c(0), c(1), c(2), c(3)},
            'node006': {c(0)}})}


s7_model = Model(
        'monte_carlo_init_macro_micro',
        [
            Component('mc', 'mc', ports=Ports(
                o_i=['pars_out'], s=['results_in'])),
            Component('init', 'init', 10, Ports(o_f=['state_out'])),
            Component('macro', 'macro', 10, Ports(
                f_init=['state_in'], o_i=['bc_out'], s=['bc_in'],
                o_f=['final_out'])),
            Component('micro', 'micro', 10, Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('mc.pars_out', 'init.muscle_settings_in'),
            Conduit('init.state_out', 'macro.state_in'),
            Conduit('macro.bc_out', 'micro.bc_in'),
            Conduit('micro.bc_out', 'macro.bc_in'),
            Conduit('macro.final_out', 'mc.results_in')])


s7_implementations = [
        Implementation(Reference('mc'), script='mc'),
        Implementation(Reference('init'), script='init'),
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro'), script='micro'),
        ]


s7_requirements = [
        ThreadedResReq(Reference('mc'), 1),
        ThreadedResReq(Reference('init'), 4),
        ThreadedResReq(Reference('macro'), 4),
        MPICoresResReq(Reference('micro'), 4)]


s7_config = Configuration(
        s7_model, None, s7_implementations, s7_requirements)


s7_resources = Resources({
        'node001': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node002': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node003': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node004': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node005': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        })


s7_solution = {
        Reference('mc'): Resources({'node001': {c(0)}}),
        Reference('init[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('init[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('init[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('init[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('init[4]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),
        Reference('init[5]'): Resources({'node003': {c(4), c(5), c(6), c(7)}}),
        Reference('init[6]'): Resources({'node004': {c(0), c(1), c(2), c(3)}}),
        Reference('init[7]'): Resources({'node004': {c(4), c(5), c(6), c(7)}}),
        Reference('init[8]'): Resources({'node005': {c(0), c(1), c(2), c(3)}}),
        Reference('init[9]'): Resources({'node005': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[4]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[5]'): Resources({'node003': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[6]'): Resources({'node004': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[7]'): Resources({'node004': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[8]'): Resources({'node005': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[9]'): Resources({'node005': {c(4), c(5), c(6), c(7)}}),
        Reference('micro[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('micro[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('micro[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('micro[4]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),
        Reference('micro[5]'): Resources({'node003': {c(4), c(5), c(6), c(7)}}),
        Reference('micro[6]'): Resources({'node004': {c(0), c(1), c(2), c(3)}}),
        Reference('micro[7]'): Resources({'node004': {c(4), c(5), c(6), c(7)}}),
        Reference('micro[8]'): Resources({'node005': {c(0), c(1), c(2), c(3)}}),
        Reference('micro[9]'): Resources({'node005': {c(4), c(5), c(6), c(7)}})}


s8_model = Model(
        'serial_micros_exclusive_macro',
        [
            Component('macro', 'macro', ports=Ports(
                o_i=['bc_out'], s=['bc_in'])),
            Component('micro1', 'micro1', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('micro2', 'micro2', ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s8_implementations = [
        Implementation(
            Reference('macro'), script='macro',
            can_share_resources=False),
        Implementation(Reference('micro1'), script='micro1'),
        Implementation(Reference('micro2'), script='micro2'),
        ]


s8_requirements = [
        ThreadedResReq(Reference('macro'), 1),
        ThreadedResReq(Reference('micro1'), 3),
        ThreadedResReq(Reference('micro2'), 2)]


s8_config = Configuration(
        s8_model, None, s8_implementations, s8_requirements)


s8_resources = Resources(
        {'node001': {c(0), c(1), c(2), c(3)}, 'node002': {c(0), c(1), c(2), c(3)}})


s8_solution = {
        Reference('macro'): Resources({'node001': {c(3)}}),
        Reference('micro1'): Resources({'node001': {c(0), c(1), c(2)}}),
        Reference('micro2'): Resources({'node001': {c(0), c(1)}})}


s9_model = Model(
        'converging_graph',
        [
            Component('e', 'e', ports=Ports(o_f=['out'])),
            Component('b', 'b', ports=Ports(
                f_init=['in1', 'in2'], o_f=['out'])),
            Component('c', 'c', ports=Ports(f_init=['in'])),
            Component('a', 'a', ports=Ports(o_f=['out'])),
            Component('d', 'd', ports=Ports(
                f_init=['in'], o_f=['out'])),
            ],
        [
            Conduit('e.out', 'b.in1'),
            Conduit('b.out', 'c.in'),
            Conduit('a.out', 'd.in'),
            Conduit('d.out', 'b.in2')])


s9_implementations = [
        Implementation(Reference('a'), script='a'),
        Implementation(Reference('b'), script='b'),
        Implementation(Reference('c'), script='c'),
        Implementation(Reference('d'), script='d'),
        Implementation(Reference('e'), script='e'),
        ]


s9_requirements = [
        ThreadedResReq(Reference('a'), 1),
        ThreadedResReq(Reference('b'), 1),
        ThreadedResReq(Reference('c'), 1),
        ThreadedResReq(Reference('d'), 1),
        ThreadedResReq(Reference('e'), 1)]


s9_config = Configuration(
        s9_model, None, s9_implementations, s9_requirements)


s9_resources = Resources({'node001': {c(0), c(1), c(2), c(3)}})


s9_solution = {
        Reference('a'): Resources({'node001': {c(1)}}),
        Reference('b'): Resources({'node001': {c(0)}}),
        Reference('c'): Resources({'node001': {c(0)}}),
        Reference('d'): Resources({'node001': {c(1)}}),
        Reference('e'): Resources({'node001': {c(0)}})}


s10_model = Model(
        'rdmc_mismatched_resources',
        [
            Component('mc', 'mc', ports=Ports(
                o_i=['pars_out'], s=['results_in'])),
            Component('rr', 'rr', ports=Ports(
                f_init=['front_in'], o_f=['front_out'],
                o_i=['back_out'], s=['back_in'])),
            Component('macro', 'macro', 8, Ports(
                f_init=['state_in'], o_i=['bc_out'], s=['bc_in'],
                o_f=['final_out'])),
            Component('micro', 'micro', 8, Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('mc.pars_out', 'rr.front_in'),
            Conduit('rr.back_out', 'macro.muscle_settings_in'),
            Conduit('macro.bc_out', 'micro.bc_in'),
            Conduit('micro.bc_out', 'macro.bc_in'),
            Conduit('macro.final_out', 'rr.back_in'),
            Conduit('rr.front_out', 'mc.results_in')])


s10_implementations = [
        Implementation(Reference('mc'), script='mc'),
        Implementation(Reference('rr'), script='rr'),
        Implementation(Reference('macro'), script='macro'),
        Implementation(Reference('micro'), script='micro'),
        ]


s10_requirements = [
        ThreadedResReq(Reference('mc'), 1),
        ThreadedResReq(Reference('rr'), 1),
        ThreadedResReq(Reference('macro'), 4),
        ThreadedResReq(Reference('micro'), 2)]


s10_config = Configuration(
        s10_model, None, s10_implementations, s10_requirements)


s10_resources = Resources({
        'node001': {
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)},
        'node002': {
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)},
        'node003': {
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)},
        })


s10_solution = {
        Reference('mc'): Resources({'node001': {c(0)}}),
        Reference('rr'): Resources({'node001': {c(0)}}),
        Reference('macro[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[2]'): Resources({'node001': {c(8), c(9), c(10), c(11)}}),
        Reference('macro[3]'): Resources({'node001': {c(12), c(13), c(14), c(15)}}),
        Reference('macro[4]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('macro[5]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('macro[6]'): Resources({'node002': {c(8), c(9), c(10), c(11)}}),
        Reference('macro[7]'): Resources({'node002': {c(12), c(13), c(14), c(15)}}),
        Reference('micro[0]'): Resources({'node001': {c(0), c(1)}}),
        Reference('micro[1]'): Resources({'node001': {c(4), c(5)}}),
        Reference('micro[2]'): Resources({'node001': {c(8), c(9)}}),
        Reference('micro[3]'): Resources({'node001': {c(12), c(13)}}),
        Reference('micro[4]'): Resources({'node002': {c(0), c(1)}}),
        Reference('micro[5]'): Resources({'node002': {c(4), c(5)}}),
        Reference('micro[6]'): Resources({'node002': {c(8), c(9)}}),
        Reference('micro[7]'): Resources({'node002': {c(12), c(13)}})}


s11_model = Model(
        'ensemble_of_dispatch_of_macro_micro',
        [
            Component('macro1', 'macro1', 3, ports=Ports(
                o_i=['bc_out'], s=['bc_in'], o_f=['state_out'])),
            Component('micro1', 'micro1', 3, ports=Ports(
                f_init=['bc_in'], o_f=['bc_out'])),
            Component('macro2', 'macro2', 3, ports=Ports(
                f_init=['state_in'], o_i=['bc_out'], s=['bc_in'])),
            Component('micro2', 'micro2', 3, ports=Ports(
                f_init=['bc_in'], o_f=['bc_out']))],
        [
            Conduit('macro1.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'macro1.bc_in'),
            Conduit('macro1.state_out', 'macro2.state_in'),
            Conduit('macro2.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'macro2.bc_in')])

s11_implementations = [
        Implementation(Reference('macro1'), script='macro'),
        Implementation(Reference('micro1'), script='micro'),
        Implementation(Reference('macro2'), script='macro'),
        Implementation(Reference('micro2'), script='micro')]


s11_requirements = [
        ThreadedResReq(Reference('macro1'), 4),
        ThreadedResReq(Reference('micro1'), 4),
        ThreadedResReq(Reference('macro2'), 4),
        ThreadedResReq(Reference('micro2'), 4),
        ]


s11_config = Configuration(s11_model, None, s11_implementations, s11_requirements)


s11_resources = Resources({
        'node001': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node002': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        })


s11_solution = {
        Reference('macro1[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro1[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro1[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('micro1[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro1[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('micro1[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('macro2[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro2[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro2[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        }


s12_model = deepcopy(s11_model)
s12_model.components[0].multiplicity = []
s12_model.components[1].multiplicity = [2]
s12_model.components[2].multiplicity = []
s12_model.components[3].multiplicity = [4]


s12_requirements = [
        ThreadedResReq(Reference('macro1'), 4),
        ThreadedResReq(Reference('micro1'), 8),
        ThreadedResReq(Reference('macro2'), 4),
        ThreadedResReq(Reference('micro2'), 4),
        ]


s12_config = Configuration(s12_model, None, s11_implementations, s12_requirements)


s12_solution = {
        Reference('macro1'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro1[0]'): Resources({'node001': {
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)}}),
        Reference('micro1[1]'): Resources({'node002': {
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)}}),
        Reference('macro2'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        }


s13_model = deepcopy(s11_model)
s13_model.components[0].multiplicity = [5]
s13_model.components[1].multiplicity = [5, 4]
s13_model.components[2].multiplicity = [5]
s13_model.components[3].multiplicity = [5, 2]


s13_requirements = [
        ThreadedResReq(Reference('macro1'), 4),
        ThreadedResReq(Reference('micro1'), 2),
        ThreadedResReq(Reference('macro2'), 4),
        ThreadedResReq(Reference('micro2'), 4),
        ]


s13_config = Configuration(s13_model, None, s11_implementations, s13_requirements)


s13_resources = Resources({
        'node001': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node002': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node003': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node004': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        'node005': {c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)},
        })


s13_solution = {
        Reference('macro1[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro1[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro1[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('macro1[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('macro1[4]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),

        Reference('micro1[0][0]'): Resources({'node001': {c(0), c(1)}}),
        Reference('micro1[0][1]'): Resources({'node001': {c(2), c(3)}}),
        Reference('micro1[0][2]'): Resources({'node003': {c(4), c(5)}}),
        Reference('micro1[0][3]'): Resources({'node003': {c(6), c(7)}}),
        Reference('micro1[1][0]'): Resources({'node001': {c(4), c(5)}}),
        Reference('micro1[1][1]'): Resources({'node001': {c(6), c(7)}}),
        Reference('micro1[1][2]'): Resources({'node004': {c(0), c(1)}}),
        Reference('micro1[1][3]'): Resources({'node004': {c(2), c(3)}}),
        Reference('micro1[2][0]'): Resources({'node002': {c(0), c(1)}}),
        Reference('micro1[2][1]'): Resources({'node002': {c(2), c(3)}}),
        Reference('micro1[2][2]'): Resources({'node004': {c(4), c(5)}}),
        Reference('micro1[2][3]'): Resources({'node004': {c(6), c(7)}}),
        Reference('micro1[3][0]'): Resources({'node002': {c(4), c(5)}}),
        Reference('micro1[3][1]'): Resources({'node002': {c(6), c(7)}}),
        Reference('micro1[3][2]'): Resources({'node005': {c(0), c(1)}}),
        Reference('micro1[3][3]'): Resources({'node005': {c(2), c(3)}}),
        Reference('micro1[4][0]'): Resources({'node003': {c(0), c(1)}}),
        Reference('micro1[4][1]'): Resources({'node003': {c(2), c(3)}}),
        Reference('micro1[4][2]'): Resources({'node005': {c(4), c(5)}}),
        Reference('micro1[4][3]'): Resources({'node005': {c(6), c(7)}}),

        Reference('macro2[0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('macro2[1]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('macro2[2]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('macro2[3]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('macro2[4]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),

        Reference('micro2[0][0]'): Resources({'node001': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[0][1]'): Resources({'node003': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[1][0]'): Resources({'node001': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[1][1]'): Resources({'node004': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[2][0]'): Resources({'node002': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[2][1]'): Resources({'node004': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[3][0]'): Resources({'node002': {c(4), c(5), c(6), c(7)}}),
        Reference('micro2[3][1]'): Resources({'node005': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[4][0]'): Resources({'node003': {c(0), c(1), c(2), c(3)}}),
        Reference('micro2[4][1]'): Resources({'node005': {c(4), c(5), c(6), c(7)}}),
        }


s14_model = Model(
        'triangle',
        [
            Component('a', 'a', ports=Ports(f_init=['in'], o_f=['out'])),
            Component('b', 'b', ports=Ports(f_init=['in'], o_f=['out'])),
            Component('c', 'c', ports=Ports(f_init=['in'], o_f=['out'])),
            ],
        [
            Conduit('a.out', 'b.in'),
            Conduit('b.out', 'c.in'),
            Conduit('c.out', 'a.in'),
            ])


s14_implementations = [
        Implementation(Reference('a'), script='a'),
        Implementation(Reference('b'), script='b'),
        Implementation(Reference('c'), script='c'),
        ]


s14_requirements = [
        ThreadedResReq(Reference('a'), 2),
        ThreadedResReq(Reference('b'), 2),
        ThreadedResReq(Reference('c'), 2),
        ]


s14_config = Configuration(
        s14_model, None, s14_implementations, s14_requirements)


s14_resources = Resources({'node001': {c(0), c(1), c(2), c(3), c(4), c(5)}})


s14_solution = RuntimeError


scenarios = [
        (s0_config, s0_resources, s0_solution),
        (s1_config, s1_resources, s1_solution),
        (s2_config, s2_resources, s2_solution),
        (s3_config, s3_resources, s3_solution),
        (s4_config, s4_resources, s4_solution),
        (s5_config, s5_resources, s5_solution),
        (s6_config, s6_resources, s6_solution),
        (s7_config, s7_resources, s7_solution),
        (s8_config, s8_resources, s8_solution),
        (s9_config, s9_resources, s9_solution),
        (s10_config, s10_resources, s10_solution),
        (s11_config, s11_resources, s11_solution),
        (s12_config, s11_resources, s12_solution),
        (s13_config, s13_resources, s13_solution),
        (s14_config, s14_resources, s14_solution),
        ]


@pytest.mark.parametrize('scenario', scenarios)
def test_scenarios(scenario: _Scenario) -> None:
    config, res, solution = scenario
    planner = Planner(res)

    if not isinstance(solution, dict):
        with pytest.raises(solution):
            planner.allocate_all(config)
        return

    allocations = planner.allocate_all(config)
    assert allocations == solution

    model_graph = ModelGraph(config.model)
    for cname, req in config.resources.items():
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
                    impl1 = config.implementations[comp1.name]
                    comp2 = [
                        c for c in model_graph.components()
                        if c.name == cname2][0]
                    impl2 = config.implementations[comp2.name]
                    assert (
                            comp2 in {c for c, _ in model_graph.successors(comp1)} or
                            comp2 in {c for c, _ in model_graph.predecessors(comp1)} or
                            (
                                comp2 in {c for c, _ in model_graph.macros(comp1)} and
                                impl2.can_share_resources and
                                impl1.can_share_resources) or
                            (
                                comp2 in {c for c, _ in model_graph.micros(comp1)} and
                                impl2.can_share_resources and
                                impl1.can_share_resources))

            elif instance1 != instance2:
                assert res1.isdisjoint(res2)
