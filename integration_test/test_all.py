import sys
from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.communicator import Message
from libmuscle.compute_element import ComputeElement
from libmuscle.muscle3 import Muscle3


def test_all(mmp_server, sys_argv_manager):
    """A positive all-up test of everything.
    """
    muscle = Muscle3()

    # create macro
    macro = ComputeElement('macro', {
            Operator.O_I: ['out[]'],
            Operator.S: ['in[]']})

    # create micros
    micros = list()
    for i in range(100):
        name = 'micro[{}]'.format(i)
        micro = ComputeElement(name, {
                Operator.F_INIT: ['in'],
                Operator.O_F: ['out']})
        micros.append(micro)

    # register submodels
    muscle.register(micros + [macro])

    # check parameters
    assert macro.get_parameter_value('test1') == 13
    assert micros[50].get_parameter_value('test3', 'str') == 'testing'
    assert micros[79].get_parameter_value('test6', '[[float]]')[0][1] == 2.0

    # send and receive some messages
    assert macro.reuse_instance()
    macro.send_message('out', Message(0.0, 10.0, 'testing'), 0)

    assert micros[0].reuse_instance()
    msg = micros[0].receive_message('in')
    assert msg.data == 'testing'
    micros[0].send_message('out', Message(0.1, None, 'testing back'))
    msg = macro.receive_message('in', 0)
    assert msg.data == 'testing back'

    macro.send_message('out', Message(10.0, None, [1, 2, 3]), 0)

    assert micros[0].reuse_instance()
    msg = micros[0].receive_message('in')
    assert msg.data == [1, 2, 3]
    micros[0].send_message('out', Message(10.1, None, 'testing back'))
    msg = macro.receive_message('in', 0)
    assert msg.data == 'testing back'

    assert not macro.reuse_instance()
    assert not micros[0].reuse_instance()
