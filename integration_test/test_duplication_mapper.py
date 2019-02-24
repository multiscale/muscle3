from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.compute_element import ComputeElement
from libmuscle.muscle3 import Muscle3


def test_duplication_mapper(mmp_server_dm, sys_argv_manager):
    """A positive all-up test of duplication mappers.

    This is an acyclic workflow.
    """
    muscle = Muscle3()

    # create elements
    duplication_mapper = ComputeElement('dm')
    first = ComputeElement('first', {Operator.F_INIT: ['in']})
    second = ComputeElement('second', {Operator.F_INIT: ['in']})

    # register submodels
    muscle.register([duplication_mapper, first, second])

    # send and receive some messages
    duplication_mapper.send_message('out1', 'testing')
    duplication_mapper.send_message('out2', 'testing')

    msg1 = first.receive_message('in', decode=True)
    msg2 = second.receive_message('in', decode=True)
    assert msg1 == 'testing'
    assert msg2 == 'testing'
