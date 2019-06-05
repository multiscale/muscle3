import sys
from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.communicator import Message
from libmuscle.compute_element import ComputeElement
from libmuscle.muscle3 import run_instances


def macro(instance_id: str):
    """Macro model implementation.
    """
    ce = ComputeElement(instance_id, {
            Operator.O_I: ['out[]'],
            Operator.S: ['in[]']})

    while ce.reuse_instance():
        # f_init
        assert ce.get_parameter_value('test1') == 13

        # o_i
        assert ce.is_vector_port('out')
        for slot in range(10):
            ce.send_message('out', Message(0.0, 10.0, 'testing'), slot)

        # s/b
        for slot in range(10):
            msg = ce.receive_message('in', slot)
            assert msg.data == 'testing back'


def micro(instance_id: str):
    """Micro model implementation.
    """
    ce = ComputeElement(instance_id, {
            Operator.F_INIT: ['in'],
            Operator.O_F: ['out']})

    while ce.reuse_instance():
        # f_init
        assert ce.get_parameter_value('test3', 'str') == 'testing'
        assert ce.get_parameter_value('test6', '[[float]]')[0][1] == 2.0

        msg = ce.receive_message('in')
        assert msg.data == 'testing'

        # o_f
        ce.send_message('out', Message(0.1, None, 'testing back'))


def test_all(log_file_in_tmpdir, mmp_server_process, sys_argv_manager):
    """A positive all-up test of everything.
    """
    submodels = {'macro': macro}
    for i in range(10):
        submodels['micro[{}]'.format(i)] = micro
    run_instances(submodels)
