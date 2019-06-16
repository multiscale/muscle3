from collections import OrderedDict
import sys
from typing import List

import pytest
from ymmsl import (ComputeElement, Conduit, Model, Operator, Reference,
                   Settings, YmmslDocument)

from libmuscle.communicator import Message
from libmuscle.instance import Instance
from muscle_manager.muscle_manager import run_simulation


def macro(instance_id: str):
    """Macro model implementation.
    """
    instance = Instance(instance_id, {
            Operator.O_I: ['out[]'],
            Operator.S: ['in[]']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_parameter_value('test1') == 13

        # o_i
        assert instance.is_vector_port('out')
        for slot in range(10):
            instance.send_message('out', Message(0.0, 10.0, 'testing'), slot)

        # s/b
        for slot in range(10):
            msg = instance.receive_message('in', slot)
            assert msg.data == 'testing back'


def micro(instance_id: str):
    """Micro model implementation.
    """
    instance = Instance(instance_id, {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_parameter_value('test3', 'str') == 'testing'
        assert instance.get_parameter_value('test4', 'bool') is True
        assert instance.get_parameter_value('test6', '[[float]]')[0][1] == 2.0

        msg = instance.receive_message('in')
        assert msg.data == 'testing'

        # o_f
        instance.send_message('out', Message(0.1, None, 'testing back'))


def test_all(log_file_in_tmpdir):
    """A positive all-up test of everything.
    """
    elements = [
            ComputeElement('macro', 'macro_implementation'),
            ComputeElement('micro', 'micro_implementation', [10])]

    conduits = [
            Conduit('macro.out', 'micro.in'),
            Conduit('micro.out', 'macro.in')]

    model = Model('test_model', elements, conduits)
    settings = Settings(OrderedDict([
                ('test1', 13),
                ('test2', 13.3),
                ('test3', 'testing'),
                ('test4', True),
                ('test5', [2.3, 5.6]),
                ('test6', [[1.0, 2.0], [3.0, 1.0]])]))

    experiment = YmmslDocument('v0.1', model, settings)
    submodels = {'macro': macro}
    for i in range(10):
        submodels['micro[{}]'.format(i)] = micro
    run_simulation(experiment, submodels)
