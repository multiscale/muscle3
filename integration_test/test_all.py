from collections import OrderedDict

import numpy as np
from ymmsl import (Component, Conduit, Configuration, Model, Operator,
                   Settings)

from libmuscle import Grid, Instance, Message
from libmuscle.runner import run_simulation


def macro():
    """Macro model implementation.
    """
    instance = Instance({
            Operator.O_I: ['out[]'],
            Operator.S: ['in[]']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_setting('test1') == 13

        # o_i
        assert instance.is_vector_port('out')
        for slot in range(10):
            instance.send('out', Message(0.0, 10.0, 'testing'), slot)

        # s/b
        for slot in range(10):
            msg = instance.receive('in', slot)
            assert msg.data['string'] == 'testing back'
            assert msg.data['int'] == 42
            assert msg.data['float'] == 3.1416
            assert msg.data['grid'].array.dtype == np.float64
            assert msg.data['grid'].array[0, 1] == 34.0


def micro():
    """Micro model implementation.
    """
    instance = Instance({
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']})

    while instance.reuse_instance():
        # f_init
        assert instance.get_setting('test3', 'str') == 'testing'
        assert instance.get_setting('test4', 'bool') is True
        assert instance.get_setting('test6', '[[float]]')[0][1] == 2.0

        msg = instance.receive('in')
        assert msg.data == 'testing'

        # o_f
        result = {
                'string': 'testing back',
                'int': 42,
                'float': 3.1416,
                'grid': Grid(np.array([[12.0, 34.0, 56.0], [1.0, 2.0, 3.0]]))}
        instance.send('out', Message(0.1, None, result))


def test_all(log_file_in_tmpdir):
    """A positive all-up test of everything.
    """
    elements = [
            Component('macro', 'macro_impl'),
            Component('micro', 'micro_impl', [10])]

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

    configuration = Configuration(model, settings)

    implementations = {'macro_impl': macro, 'micro_impl': micro}
    run_simulation(configuration, implementations)
