from copy import deepcopy

import pytest
from ymmsl.v0_2 import (
        Component, Conduit, Configuration, Model, MPICoresResReq, Ports, Program,
        Reference, ResourceRequirements, ThreadedResReq)

from libmuscle.planner.planner import ModelGraph, Planner, ResourceAssignment
from libmuscle.planner.resources import Resources

from libmuscle.test.conftest import core as c, on_node_resources as onr, resources


_ResReqs = dict[Reference, ResourceRequirements]


_Scenario = tuple[Configuration, Resources]


s0_model = Model(
        'semidetached_macro_micro', None, '', None,
        [
            Component('macro', Ports(o_i=['out']), '', 'macro'),
            Component('micro', Ports(f_init=['in']), '', 'micro')],
        [
            Conduit('macro.out', 'micro.in')])


s0_programs = [
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro'), script='micro')]


s0_requirements = [
        ThreadedResReq(Reference('semidetached_macro_micro.macro'), 2),
        ThreadedResReq(Reference('semidetached_macro_micro.micro'), 2)]


s0_config = Configuration(
        's0', [], [s0_model], None, None, s0_programs, s0_requirements)


s0_resources = resources({'node001': [c(0), c(1), c(2), c(3)]})


s0_solution = {
        Reference('macro'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('micro'): ResourceAssignment([onr('node001', {2, 3})])}


s1_model = Model(
        'serial_micros', None, '', None,
        [
            Component(
                'macro', Ports(o_i=['bc_out'], s=['bc_in']), '', 'macro'),
            Component(
                'micro1', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro1'),
            Component(
                'micro2', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro2'),
            Component(
                'micro3', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro3')],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'micro3.bc_in'),
            Conduit('micro3.bc_out', 'macro.bc_in')])


s1_programs = [
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro1'), script='micro1'),
        Program(Reference('micro2'), script='micro2'),
        Program(Reference('micro3'), script='micro3'),
        ]


s1_requirements = [
        ThreadedResReq(Reference('serial_micros.macro'), 4),
        ThreadedResReq(Reference('serial_micros.micro1'), 2),
        ThreadedResReq(Reference('serial_micros.micro2'), 2),
        ThreadedResReq(Reference('serial_micros.micro3'), 1)]


s1_config = Configuration(
        's1', [], [s1_model], None, None, s1_programs, s1_requirements)


s1_resources = resources({'node001': [c(0), c(1), c(2), c(3)]})


s1_solution = {
        Reference('macro'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro1'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('micro2'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('micro3'): ResourceAssignment([onr('node001', 0)])}


s2_model = Model(
        'parallel_micros', None, '', None,
        [
            Component('macro', Ports(o_i=['bc_out'], s=['bc_in']), '', 'macro'),
            Component('micro1', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro1'),
            Component('micro2', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro2')],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('macro.bc_out', 'micro2.bc_in'),
            Conduit('micro1.bc_out', 'macro.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s2_programs = [
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro1'), script='micro1'),
        Program(Reference('micro2'), script='micro2'),
        ]


s2_requirements = [
        ThreadedResReq(Reference('parallel_micros.macro'), 1),
        ThreadedResReq(Reference('parallel_micros.micro1'), 3),
        ThreadedResReq(Reference('parallel_micros.micro2'), 2)]


s2_config = Configuration(
        's2', [], [s2_model], None, None, s2_programs, s2_requirements)


s2_resources = resources(
        {'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)]})


s2_solution = {
        Reference('macro'): ResourceAssignment([onr('node001', 0)]),
        Reference('micro1'): ResourceAssignment([onr('node001', {0, 1, 2})]),
        Reference('micro2'): ResourceAssignment([onr('node002', {0, 1})])}


s3_model = Model(
        'diamond', None, '', None,
        [
            Component('a', Ports(o_f=['out']), '', 'a'),
            Component('b1', Ports(f_init=['in'], o_f=['out']), '', 'b1'),
            Component('b2', Ports(f_init=['in'], o_f=['out']), '', 'b2'),
            Component('c', Ports(f_init=['in'], o_f=['bc_out']), '', 'c')
            ],
        [
            Conduit('a.out', 'b1.in'),
            Conduit('a.out', 'b2.in'),
            Conduit('b1.out', 'c.in'),
            Conduit('b2.out', 'c.in')])


s3_programs = [
        Program(Reference('a'), script='a'),
        Program(Reference('b1'), script='b'),
        Program(Reference('b2'), script='b'),
        Program(Reference('c'), script='c'),
        ]


s3_requirements = [
        ThreadedResReq(Reference('diamond.a'), 1),
        MPICoresResReq(Reference('diamond.b1'), 6),
        ThreadedResReq(Reference('diamond.b2'), 2),
        ThreadedResReq(Reference('diamond.c'), 4)]


s3_config = Configuration(
        's3', [], [s3_model], None, None, s3_programs, s3_requirements)


s3_resources = resources(
        {'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)]})


s3_solution = {
        Reference('a'): ResourceAssignment([onr('node001', 0)]),
        Reference('b1'): ResourceAssignment([
            onr('node001', 2), onr('node001', 3), onr('node002', 0), onr('node002', 1),
            onr('node002', 2), onr('node002', 3)]),
        Reference('b2'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('c'): ResourceAssignment([onr('node001', {0, 1, 2, 3})])}


s4_model = Model(
        'lockstep_macros_micro', None, '', None,
        [
            Component(
                'macro1', Ports(o_i=['bc_out'], s=['bc_in']), '', 'macro1'),
            Component(
                'macro2', Ports(o_i=['bc_out'], s=['bc_in']), '', 'macro2'),
            Component(
                'micro', Ports(f_init=['bc_in1', 'bc_in2'], o_f=['bc_out1', 'bc_out2']),
                '', 'micro')],
        [
            Conduit('macro1.bc_out', 'micro.bc_in1'),
            Conduit('macro2.bc_out', 'micro.bc_in2'),
            Conduit('micro.bc_out1', 'macro1.bc_in'),
            Conduit('micro.bc_out1', 'macro2.bc_in')])


s4_programs = [
        Program(Reference('macro1'), script='macro1'),
        Program(Reference('macro2'), script='macro2'),
        Program(Reference('micro'), script='micro'),
        ]


s4_requirements = [
        ThreadedResReq(Reference('lockstep_macros_micro.macro1'), 2),
        ThreadedResReq(Reference('lockstep_macros_micro.macro2'), 3),
        ThreadedResReq(Reference('lockstep_macros_micro.micro'), 3)]


s4_config = Configuration(
        's4', [], [s4_model], None, None, s4_programs, s4_requirements)


s4_resources = resources(
        {'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)]})


s4_solution = {
        Reference('macro1'): ResourceAssignment([onr('node002', {0, 1})]),
        Reference('macro2'): ResourceAssignment([onr('node001', {0, 1, 2})]),
        Reference('micro'): ResourceAssignment([onr('node001', {0, 1, 2})])}


s5_model = Model(
        'repeater_model', None, '', None,
        [
            Component('init', Ports(o_f=['out1', 'out2']), '', 'init'),
            Component(
                'macro', Ports(f_init=['in'], o_i=['bc_out'], s=['bc_in']), '', 'macro'
                ),
            Component('micro', Ports(f_init=['in', 'in2'], o_f=['out']), '', 'micro'),
            Component(
                'repeater', Ports(
                    f_init=['data_in'], o_i=['data_out', 'trigger_out'],
                    s=['trigger_in']),
                '', 'repeater')],
        [
            Conduit('init.out1', 'macro.in'),
            Conduit('init.out2', 'repeater.data_in'),
            Conduit('macro.bc_out', 'repeater.trigger_in'),
            Conduit('repeater.trigger_out', 'micro.in'),
            Conduit('repeater.data_out', 'micro.in2'),
            Conduit('micro.out', 'macro.bc_in')])


s5_programs = [
        Program(Reference('init'), script='init'),
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro'), script='micro'),
        Program(Reference('repeater'), script='repeater'),
        ]


s5_requirements = [
        ThreadedResReq(Reference('repeater_model.init'), 4),
        MPICoresResReq(Reference('repeater_model.repeater'), 1),
        ThreadedResReq(Reference('repeater_model.macro'), 4),
        ThreadedResReq(Reference('repeater_model.micro'), 4)]


s5_config = Configuration(
        's5', [], [s5_model], None, None, s5_programs, s5_requirements)


s5_resources = resources({
    'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)],
    'node003': [c(0), c(1)]})


# This is inefficient, as the models can all share resources. But repeater
# is funny, and the algorithm cannot deal with it yet. It does give a valid
# result with no overlap, so we'll accept that for the time being.
s5_solution = {
        Reference('init'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('repeater'): ResourceAssignment([onr('node003', 0)])}


s6_model = Model(
        'scale_overlap', None, '', None,
        [
            Component('a', Ports(o_i=['bc_out'], s=['bc_in']), '', 'a'),
            Component(
                'tcf', Ports(o_i=['a_out', 'b_out'], s=['a_in', 'b_in']), '', 'tcf'),
            Component('b', Ports(o_i=['bc_out'], s=['bc_in']), '', 'b')],
        [
            Conduit('a.bc_out', 'tcf.a_in'),
            Conduit('tcf.a_out', 'a.bc_in'),
            Conduit('b.bc_out', 'tcf.b_in'),
            Conduit('tcf.b_out', 'b.bc_in')])


s6_programs = [
        Program(Reference('a'), script='a'),
        Program(Reference('tcf'), script='tcf'),
        Program(Reference('b'), script='b'),
        ]


s6_requirements = [
        ThreadedResReq(Reference('scale_overlap.a'), 4),
        MPICoresResReq(Reference('scale_overlap.b'), 16),
        ThreadedResReq(Reference('scale_overlap.tcf'), 1)]


s6_config = Configuration(
        's6', [], [s6_model], None, None, s6_programs, s6_requirements)


s6_resources = resources({
        'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)],
        'node003': [c(0), c(1), c(2), c(3)], 'node004': [c(0), c(1), c(2), c(3)],
        'node005': [c(0), c(1), c(2), c(3)], 'node006': [c(0), c(1), c(2), c(3)]
        })


s6_solution = {
        Reference('a'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('tcf'): ResourceAssignment([onr('node002', 0)]),
        Reference('b'): ResourceAssignment([
            onr('node002', 1), onr('node002', 2), onr('node002', 3), onr('node003', 0),
            onr('node003', 1), onr('node003', 2), onr('node003', 3), onr('node004', 0),
            onr('node004', 1), onr('node004', 2), onr('node004', 3), onr('node005', 0),
            onr('node005', 1), onr('node005', 2), onr('node005', 3), onr('node006', 0)])
        }


s7_model = Model(
        'monte_carlo_init_macro_micro', None, '', None,
        [
            Component('mc', Ports(o_i=['pars_out'], s=['results_in']), '', 'mc'),
            Component('init', Ports(o_f=['state_out']), '', 'init', False, 10),
            Component(
                'macro', Ports(
                    f_init=['state_in'], o_i=['bc_out'], s=['bc_in'],
                    o_f=['final_out']),
                '', 'macro', False, 10),
            Component(
                'micro', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro', False,
                10)],
        [
            Conduit('mc.pars_out', 'init.muscle_settings_in'),
            Conduit('init.state_out', 'macro.state_in'),
            Conduit('macro.bc_out', 'micro.bc_in'),
            Conduit('micro.bc_out', 'macro.bc_in'),
            Conduit('macro.final_out', 'mc.results_in')])


s7_programs = [
        Program(Reference('mc'), script='mc'),
        Program(Reference('init'), script='init'),
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro'), script='micro'),
        ]


s7_requirements = [
        ThreadedResReq(Reference('monte_carlo_init_macro_micro.mc'), 1),
        ThreadedResReq(Reference('monte_carlo_init_macro_micro.init'), 4),
        ThreadedResReq(Reference('monte_carlo_init_macro_micro.macro'), 4),
        MPICoresResReq(Reference('monte_carlo_init_macro_micro.micro'), 4)]


s7_config = Configuration(
        's7', [], [s7_model], None, None, s7_programs, s7_requirements)


s7_resources = resources({
        'node001': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node002': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node003': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node004': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node005': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        })


s7_solution = {
        Reference('mc'): ResourceAssignment([onr('node001', 0)]),

        Reference('init[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('init[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('init[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('init[3]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('init[4]'): ResourceAssignment([onr('node003', {0, 1, 2, 3})]),
        Reference('init[5]'): ResourceAssignment([onr('node003', {4, 5, 6, 7})]),
        Reference('init[6]'): ResourceAssignment([onr('node004', {0, 1, 2, 3})]),
        Reference('init[7]'): ResourceAssignment([onr('node004', {4, 5, 6, 7})]),
        Reference('init[8]'): ResourceAssignment([onr('node005', {0, 1, 2, 3})]),
        Reference('init[9]'): ResourceAssignment([onr('node005', {4, 5, 6, 7})]),

        Reference('macro[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('macro[3]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('macro[4]'): ResourceAssignment([onr('node003', {0, 1, 2, 3})]),
        Reference('macro[5]'): ResourceAssignment([onr('node003', {4, 5, 6, 7})]),
        Reference('macro[6]'): ResourceAssignment([onr('node004', {0, 1, 2, 3})]),
        Reference('macro[7]'): ResourceAssignment([onr('node004', {4, 5, 6, 7})]),
        Reference('macro[8]'): ResourceAssignment([onr('node005', {0, 1, 2, 3})]),
        Reference('macro[9]'): ResourceAssignment([onr('node005', {4, 5, 6, 7})]),

        Reference('micro[0]'): ResourceAssignment([
            onr('node001', 0), onr('node001', 1), onr('node001', 2),
            onr('node001', 3)]),
        Reference('micro[1]'): ResourceAssignment([
            onr('node001', 4), onr('node001', 5), onr('node001', 6),
            onr('node001', 7)]),
        Reference('micro[2]'): ResourceAssignment([
            onr('node002', 0), onr('node002', 1), onr('node002', 2),
            onr('node002', 3)]),
        Reference('micro[3]'): ResourceAssignment([
            onr('node002', 4), onr('node002', 5), onr('node002', 6),
            onr('node002', 7)]),
        Reference('micro[4]'): ResourceAssignment([
            onr('node003', 0), onr('node003', 1), onr('node003', 2),
            onr('node003', 3)]),
        Reference('micro[5]'): ResourceAssignment([
            onr('node003', 4), onr('node003', 5), onr('node003', 6),
            onr('node003', 7)]),
        Reference('micro[6]'): ResourceAssignment([
            onr('node004', 0), onr('node004', 1), onr('node004', 2),
            onr('node004', 3)]),
        Reference('micro[7]'): ResourceAssignment([
            onr('node004', 4), onr('node004', 5), onr('node004', 6),
            onr('node004', 7)]),
        Reference('micro[8]'): ResourceAssignment([
            onr('node005', 0), onr('node005', 1), onr('node005', 2),
            onr('node005', 3)]),
        Reference('micro[9]'): ResourceAssignment([
            onr('node005', 4), onr('node005', 5), onr('node005', 6),
            onr('node005', 7)])}


s8_model = Model(
        'serial_micros_exclusive_macro', None, '', None,
        [
            Component('macro', Ports(o_i=['bc_out'], s=['bc_in']), '', 'macro'),
            Component('micro1', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro1'),
            Component('micro2', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro2')],
        [
            Conduit('macro.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'macro.bc_in')])


s8_programs = [
        Program(
            Reference('macro'), script='macro',
            can_share_resources=False),
        Program(Reference('micro1'), script='micro1'),
        Program(Reference('micro2'), script='micro2'),
        ]


s8_requirements = [
        ThreadedResReq(Reference('serial_micros_exclusive_macro.macro'), 1),
        ThreadedResReq(Reference('serial_micros_exclusive_macro.micro1'), 3),
        ThreadedResReq(Reference('serial_micros_exclusive_macro.micro2'), 2)]


s8_config = Configuration(
        's8', [], [s8_model], None, None, s8_programs, s8_requirements)


s8_resources = resources(
        {'node001': [c(0), c(1), c(2), c(3)], 'node002': [c(0), c(1), c(2), c(3)]})


s8_solution = {
        Reference('macro'): ResourceAssignment([onr('node001', 3)]),
        Reference('micro1'): ResourceAssignment([onr('node001', {0, 1, 2})]),
        Reference('micro2'): ResourceAssignment([onr('node001', {0, 1})])}


s9_model = Model(
        'converging_graph', None, '', None,
        [
            Component('e', Ports(o_f=['out']), '', 'e'),
            Component('b', Ports(f_init=['in1', 'in2'], o_f=['out']), '', 'b'),
            Component('c', Ports(f_init=['in']), '', 'c'),
            Component('a', Ports(o_f=['out']), '', 'a'),
            Component('d', Ports(f_init=['in'], o_f=['out']), '', 'd'),
            ],
        [
            Conduit('e.out', 'b.in1'),
            Conduit('b.out', 'c.in'),
            Conduit('a.out', 'd.in'),
            Conduit('d.out', 'b.in2')])


s9_programs = [
        Program(Reference('a'), script='a'),
        Program(Reference('b'), script='b'),
        Program(Reference('c'), script='c'),
        Program(Reference('d'), script='d'),
        Program(Reference('e'), script='e'),
        ]


s9_requirements = [
        ThreadedResReq(Reference('converging_graph.a'), 1),
        ThreadedResReq(Reference('converging_graph.b'), 1),
        ThreadedResReq(Reference('converging_graph.c'), 1),
        ThreadedResReq(Reference('converging_graph.d'), 1),
        ThreadedResReq(Reference('converging_graph.e'), 1)]


s9_config = Configuration(
        's9', [], [s9_model], None, None, s9_programs, s9_requirements)


s9_resources = resources({'node001': [c(0), c(1), c(2), c(3)]})


s9_solution = {
        Reference('a'): ResourceAssignment([onr('node001', 1)]),
        Reference('b'): ResourceAssignment([onr('node001', 0)]),
        Reference('c'): ResourceAssignment([onr('node001', 0)]),
        Reference('d'): ResourceAssignment([onr('node001', 1)]),
        Reference('e'): ResourceAssignment([onr('node001', 0)])}


s10_model = Model(
        'rdmc_mismatched_resources', None, '', None,
        [
            Component('mc', Ports(o_i=['pars_out'], s=['results_in']), '', 'mc'),
            Component(
                'rr', Ports(
                    f_init=['front_in'], o_f=['front_out'],
                    o_i=['back_out'], s=['back_in']),
                '', 'rr'),
            Component(
                'macro', Ports(
                    f_init=['state_in'], o_i=['bc_out'], s=['bc_in'],
                    o_f=['final_out']),
                '', 'macro', False, 8),
            Component(
                'micro', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro', False,
                8)],
        [
            Conduit('mc.pars_out', 'rr.front_in'),
            Conduit('rr.back_out', 'macro.muscle_settings_in'),
            Conduit('macro.bc_out', 'micro.bc_in'),
            Conduit('micro.bc_out', 'macro.bc_in'),
            Conduit('macro.final_out', 'rr.back_in'),
            Conduit('rr.front_out', 'mc.results_in')])


s10_programs = [
        Program(Reference('mc'), script='mc'),
        Program(Reference('rr'), script='rr'),
        Program(Reference('macro'), script='macro'),
        Program(Reference('micro'), script='micro'),
        ]


s10_requirements = [
        ThreadedResReq(Reference('rdmc_mismatched_resources.mc'), 1),
        ThreadedResReq(Reference('rdmc_mismatched_resources.rr'), 1),
        ThreadedResReq(Reference('rdmc_mismatched_resources.macro'), 4),
        ThreadedResReq(Reference('rdmc_mismatched_resources.micro'), 2)]


s10_config = Configuration(
        's10', [], [s10_model], None, None, s10_programs, s10_requirements)


s10_resources = resources({
        'node001': [
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)],
        'node002': [
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)],
        'node003': [
            c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7),
            c(8), c(9), c(10), c(11), c(12), c(13), c(14), c(15)],
        })


s10_solution = {
        Reference('mc'): ResourceAssignment([onr('node001', 0)]),
        Reference('rr'): ResourceAssignment([onr('node001', 0)]),

        Reference('macro[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro[2]'): ResourceAssignment([onr('node001', {8, 9, 10, 11})]),
        Reference('macro[3]'): ResourceAssignment([onr('node001', {12, 13, 14, 15})]),
        Reference('macro[4]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('macro[5]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('macro[6]'): ResourceAssignment([onr('node002', {8, 9, 10, 11})]),
        Reference('macro[7]'): ResourceAssignment([onr('node002', {12, 13, 14, 15})]),

        Reference('micro[0]'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('micro[1]'): ResourceAssignment([onr('node001', {4, 5})]),
        Reference('micro[2]'): ResourceAssignment([onr('node001', {8, 9})]),
        Reference('micro[3]'): ResourceAssignment([onr('node001', {12, 13})]),
        Reference('micro[4]'): ResourceAssignment([onr('node002', {0, 1})]),
        Reference('micro[5]'): ResourceAssignment([onr('node002', {4, 5})]),
        Reference('micro[6]'): ResourceAssignment([onr('node002', {8, 9})]),
        Reference('micro[7]'): ResourceAssignment([onr('node002', {12, 13})])}


s11_model = Model(
        'ensemble_of_dispatch_of_macro_micro', None, '', None,
        [
            Component(
                'macro1', Ports(o_i=['bc_out'], s=['bc_in'], o_f=['state_out']), '',
                'macro1', False, 3),
            Component(
                'micro1', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro1', False,
                3),
            Component(
                'macro2', Ports(f_init=['state_in'], o_i=['bc_out'], s=['bc_in']), '',
                'macro2', False, 3),
            Component(
                'micro2', Ports(f_init=['bc_in'], o_f=['bc_out']), '', 'micro2', False,
                3)],
        [
            Conduit('macro1.bc_out', 'micro1.bc_in'),
            Conduit('micro1.bc_out', 'macro1.bc_in'),
            Conduit('macro1.state_out', 'macro2.state_in'),
            Conduit('macro2.bc_out', 'micro2.bc_in'),
            Conduit('micro2.bc_out', 'macro2.bc_in')])

s11_programs = [
        Program(Reference('macro1'), script='macro'),
        Program(Reference('micro1'), script='micro'),
        Program(Reference('macro2'), script='macro'),
        Program(Reference('micro2'), script='micro')]


s11_requirements = [
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro1'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro1'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro2'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro2'), 4),
        ]


s11_config = Configuration(
        's11', [], [s11_model], None, None, s11_programs, s11_requirements)


s11_resources = resources({
        'node001': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node002': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        })


s11_solution = {
        Reference('macro1[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro1[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro1[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('micro1[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro1[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('micro1[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('macro2[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro2[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro2[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('micro2[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro2[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('micro2[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})])}


s12_model = deepcopy(s11_model)
s12_model.components[Reference('macro1')].multiplicity = []
s12_model.components[Reference('micro1')].multiplicity = [2]
s12_model.components[Reference('macro2')].multiplicity = []
s12_model.components[Reference('micro2')].multiplicity = [4]


s12_requirements = [
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro1'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro1'), 8),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro2'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro2'), 4),
        ]


s12_config = Configuration(
        's12', [], [s12_model], None, None, s11_programs, s12_requirements)


s12_solution = {
        Reference('macro1'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro1[0]'): ResourceAssignment([
            onr('node001', {0, 1, 2, 3, 4, 5, 6, 7})]),
        Reference('micro1[1]'): ResourceAssignment([
            onr('node002', {0, 1, 2, 3, 4, 5, 6, 7})]),
        Reference('macro2'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro2[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro2[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('micro2[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('micro2[3]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        }


s13_model = deepcopy(s11_model)
s13_model.components[Reference('macro1')].multiplicity = [5]
s13_model.components[Reference('micro1')].multiplicity = [5, 4]
s13_model.components[Reference('macro2')].multiplicity = [5]
s13_model.components[Reference('micro2')].multiplicity = [5, 2]


s13_requirements = [
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro1'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro1'), 2),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.macro2'), 4),
        ThreadedResReq(Reference('ensemble_of_dispatch_of_macro_micro.micro2'), 4),
        ]


s13_config = Configuration(
        's13', [], [s13_model], None, None, s11_programs, s13_requirements)


s13_resources = resources({
        'node001': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node002': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node003': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node004': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        'node005': [c(0), c(1), c(2), c(3), c(4), c(5), c(6), c(7)],
        })


s13_solution = {
        Reference('macro1[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro1[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro1[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('macro1[3]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('macro1[4]'): ResourceAssignment([onr('node003', {0, 1, 2, 3})]),

        Reference('micro1[0][0]'): ResourceAssignment([onr('node001', {0, 1})]),
        Reference('micro1[0][1]'): ResourceAssignment([onr('node001', {2, 3})]),
        Reference('micro1[0][2]'): ResourceAssignment([onr('node003', {4, 5})]),
        Reference('micro1[0][3]'): ResourceAssignment([onr('node003', {6, 7})]),
        Reference('micro1[1][0]'): ResourceAssignment([onr('node001', {4, 5})]),
        Reference('micro1[1][1]'): ResourceAssignment([onr('node001', {6, 7})]),
        Reference('micro1[1][2]'): ResourceAssignment([onr('node004', {0, 1})]),
        Reference('micro1[1][3]'): ResourceAssignment([onr('node004', {2, 3})]),
        Reference('micro1[2][0]'): ResourceAssignment([onr('node002', {0, 1})]),
        Reference('micro1[2][1]'): ResourceAssignment([onr('node002', {2, 3})]),
        Reference('micro1[2][2]'): ResourceAssignment([onr('node004', {4, 5})]),
        Reference('micro1[2][3]'): ResourceAssignment([onr('node004', {6, 7})]),
        Reference('micro1[3][0]'): ResourceAssignment([onr('node002', {4, 5})]),
        Reference('micro1[3][1]'): ResourceAssignment([onr('node002', {6, 7})]),
        Reference('micro1[3][2]'): ResourceAssignment([onr('node005', {0, 1})]),
        Reference('micro1[3][3]'): ResourceAssignment([onr('node005', {2, 3})]),
        Reference('micro1[4][0]'): ResourceAssignment([onr('node003', {0, 1})]),
        Reference('micro1[4][1]'): ResourceAssignment([onr('node003', {2, 3})]),
        Reference('micro1[4][2]'): ResourceAssignment([onr('node005', {4, 5})]),
        Reference('micro1[4][3]'): ResourceAssignment([onr('node005', {6, 7})]),

        Reference('macro2[0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('macro2[1]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('macro2[2]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('macro2[3]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('macro2[4]'): ResourceAssignment([onr('node003', {0, 1, 2, 3})]),

        Reference('micro2[0][0]'): ResourceAssignment([onr('node001', {0, 1, 2, 3})]),
        Reference('micro2[0][1]'): ResourceAssignment([onr('node003', {4, 5, 6, 7})]),
        Reference('micro2[1][0]'): ResourceAssignment([onr('node001', {4, 5, 6, 7})]),
        Reference('micro2[1][1]'): ResourceAssignment([onr('node004', {0, 1, 2, 3})]),
        Reference('micro2[2][0]'): ResourceAssignment([onr('node002', {0, 1, 2, 3})]),
        Reference('micro2[2][1]'): ResourceAssignment([onr('node004', {4, 5, 6, 7})]),
        Reference('micro2[3][0]'): ResourceAssignment([onr('node002', {4, 5, 6, 7})]),
        Reference('micro2[3][1]'): ResourceAssignment([onr('node005', {0, 1, 2, 3})]),
        Reference('micro2[4][0]'): ResourceAssignment([onr('node003', {0, 1, 2, 3})]),
        Reference('micro2[4][1]'): ResourceAssignment([onr('node005', {4, 5, 6, 7})]),
        }


s14_model = Model(
        'triangle', None, '', None,
        [
            Component('a', Ports(f_init=['in'], o_f=['out']), '', 'a'),
            Component('b', Ports(f_init=['in'], o_f=['out']), '', 'b'),
            Component('c', Ports(f_init=['in'], o_f=['out']), '', 'c'),
            ],
        [
            Conduit('a.out', 'b.in'),
            Conduit('b.out', 'c.in'),
            Conduit('c.out', 'a.in'),
            ])


s14_programs = [
        Program(Reference('a'), script='a'),
        Program(Reference('b'), script='b'),
        Program(Reference('c'), script='c'),
        ]


s14_requirements = [
        ThreadedResReq(Reference('triangle.a'), 2),
        ThreadedResReq(Reference('triangle.b'), 2),
        ThreadedResReq(Reference('triangle.c'), 2),
        ]


s14_config = Configuration(
        's14', [], [s14_model], None, None, s14_programs, s14_requirements)


s14_resources = resources({'node001': [c(0), c(1), c(2), c(3), c(4), c(5)]})


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

    model_graph = ModelGraph(config.root_model())
    for cname, req in config.resources.items():
        # check that we have enough cores
        component = [
            c for c in model_graph.components()
            if c.name == cname[1:]][0]

        if isinstance(req, ThreadedResReq):
            for instance in component.instances():
                assert len(allocations[instance].by_rank) == 1
                assert allocations[instance].by_rank[0].total_cores() == req.threads
        elif isinstance(req, MPICoresResReq):
            for instance in component.instances():
                nranks = len(allocations[instance].by_rank)
                assert nranks == req.mpi_processes
                for r in range(nranks):
                    assert allocations[instance].by_rank[r].total_cores() == 1

    # check for any overlapping instances
    for instance1, res_asm1 in allocations.items():
        for instance2, res_asm2 in allocations.items():
            res1 = res_asm1.as_resources()
            res2 = res_asm2.as_resources()
            cname1 = instance1.without_trailing_ints()
            cname2 = instance2.without_trailing_ints()
            if cname1 != cname2:
                if not res1.isdisjoint(res2):
                    comp1 = [
                        c for c in model_graph.components()
                        if c.name == cname1][0]
                    program1 = config.programs[comp1.name]
                    comp2 = [
                        c for c in model_graph.components()
                        if c.name == cname2][0]
                    program2 = config.programs[comp2.name]
                    assert (
                            comp2 in {c for c, _ in model_graph.successors(comp1)} or
                            comp2 in {c for c, _ in model_graph.predecessors(comp1)} or
                            (
                                comp2 in {c for c, _ in model_graph.macros(comp1)} and
                                program2.can_share_resources and
                                program1.can_share_resources) or
                            (
                                comp2 in {c for c, _ in model_graph.micros(comp1)} and
                                program2.can_share_resources and
                                program1.can_share_resources))

            elif instance1 != instance2:
                assert res1.isdisjoint(res2)
