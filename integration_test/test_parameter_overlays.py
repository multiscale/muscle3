import sys
from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.communicator import Message
from libmuscle.compute_element import ComputeElement
from libmuscle.configuration import Configuration
from libmuscle.muscle3 import run_instances


def qmc(instance_id: str):
    """qMC implementation.
    """
    ce = ComputeElement(instance_id, {Operator.O_F: ['parameters_out[]']})

    while ce.reuse_instance():
        # o_f
        config0 = Configuration.from_plain_dict({'test2': 14.4})

        assert ce.is_connected('parameters_out')
        assert ce.is_vector_port('parameters_out')
        assert not ce.is_resizable('parameters_out')
        length = ce.get_port_length('parameters_out')
        assert length == 10
        for slot in range(length):
            ce.send_message('parameters_out',
                            Message(0.0, None, config0), slot)


def macro(instance_id: str):
    """Macro model implementation.
    """
    ce = ComputeElement(instance_id, {
            Operator.O_I: ['out'], Operator.S: ['in']})

    while ce.reuse_instance():
        # f_init
        assert ce.get_parameter_value('test2') == 14.4
        # o_i
        ce.send_message('out', Message(0.0, 10.0, 'testing'))
        # s/b
        msg = ce.receive_message('in')
        assert msg.data == 'testing back'


def micro(instance_id: str):
    """Micro model implementation.
    """
    ce = ComputeElement(instance_id, {
            Operator.F_INIT: ['in'], Operator.O_F: ['out']})

    assert ce.get_parameter_value('test2') == 13.3
    while ce.reuse_instance():
        # f_init
        assert ce.get_parameter_value('test2', 'float') == 14.4
        msg = ce.receive_message('in')
        assert msg.data == 'testing'

        # with pytest.raises(RuntimeError):
        #     ce.receive_message_with_parameters('in')

        # o_f
        ce.send_message('out', Message(0.1, None, 'testing back'))


def explicit_micro(instance_id: str):
    """Micro model implementation with explicit parameters.

    Receives overlay parameters explicitly, rather than having MUSCLE
    handle them.
    """
    ce = ComputeElement(instance_id, {
            Operator.F_INIT: ['in'], Operator.O_F: ['out']})

    while ce.reuse_instance(False):
        # f_init
        assert ce.get_parameter_value('test2', 'float') == 13.3
        msg = ce.receive_message_with_parameters('in')
        assert msg.data == 'testing'
        assert msg.configuration['test2'] == 14.4
        assert ce.get_parameter_value('test2') == 13.3

        # o_f
        ce.send_message(
                'out', Message(0.1, None, 'testing back', msg.configuration))


def test_parameter_overlays(log_file_in_tmpdir, mmp_server_process_qmc,
                            sys_argv_manager):
    """A positive all-up test of parameter overlays.
    """
    submodels = {'qmc': qmc}
    for i in range(9):
        submodels['macro[{}]'.format(i)] = macro
        submodels['micro[{}]'.format(i)] = micro
    submodels['macro[9]'] = macro
    submodels['micro[9]'] = explicit_micro
    run_instances(submodels)
