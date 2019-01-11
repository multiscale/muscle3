import sys

import pytest
from ymmsl import Operator, Reference

from libmuscle.compute_element import ComputeElement
from libmuscle.muscle3 import Muscle3


@pytest.fixture
def sys_argv_manager():
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield
    sys.argv = old_argv


def test_all(mmp_server, sys_argv_manager):
    """A positive all-up test of everything.
    """
    muscle = Muscle3()

    # create macro
    macro = ComputeElement('macro', {
            Operator.O_I: ['out'],
            Operator.S: ['in']})

    # create micros
    micros = list()
    for i in range(100):
        name = 'micro[{}][{}]'.format(i // 10, i % 10)
        micro = ComputeElement(name, {
                Operator.F_INIT: ['in'],
                Operator.O_F: ['out']})
        micros.append(micro)

    # register submodels
    muscle.register(micros + [macro])

    # send and receive some messages
    macro.send_message('out', 'testing', [0, 0])
    msg = micros[0].receive_message('in', True)
    assert msg == 'testing'

    micros[0].send_message('out', 'testing back')
    msg = macro.receive_message('in', True, [0, 0])
    assert msg == 'testing back'

    macro.send_message('out', [1, 2, 3], [3, 4])
    msg = micros[34].receive_message('in', True)
    assert msg == [1, 2, 3]
