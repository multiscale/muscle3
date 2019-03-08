import sys
from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.communicator import Message
from libmuscle.compute_element import ComputeElement
from libmuscle.configuration import Configuration
from libmuscle.muscle3 import Muscle3


@pytest.fixture
def sys_argv_manager():
    old_argv = sys.argv
    sys.argv = ['', '--muscle-manager=localhost:9000']
    yield
    sys.argv = old_argv


def test_parameter_overlays(mmp_server_qmc, sys_argv_manager):
    """A positive all-up test of parameter overlays.
    """
    muscle = Muscle3()

    # create qMC
    qmc = ComputeElement('qmc', {Operator.O_F: ['parameters_out[]']})

    # create macros
    macros = list()
    for i in range(100):
        name = 'macro[{}]'.format(i)
        macro = ComputeElement(name, {
            Operator.O_I: ['out'],
            Operator.S: ['in']})
        macros.append(macro)

    # create micros
    micros = list()
    for i in range(100):
        name = 'micro[{}]'.format(i)
        micro = ComputeElement(name, {
                Operator.F_INIT: ['in'],
                Operator.O_F: ['out']})
        micros.append(micro)

    # register submodels
    muscle.register([qmc] + macros + micros)

    # check parameters
    assert macro.get_parameter_value('test2') == 13.3

    # send and receive some messages
    config0 = Configuration.from_plain_dict({'test2': 14.4})
    assert qmc.reuse_instance()
    qmc.send_message('parameters_out', Message(0.0, None, config0), 0)

    assert macros[0].reuse_instance()
    assert macros[0].get_parameter_value('test2') == 14.4

    macros[0].send_message('out', Message(0.0, 1.0, 'testing'))
    assert micros[0].reuse_instance()
    msg = micros[0].receive_message('in')
    assert msg.data == 'testing'
    assert micros[0].get_parameter_value('test2') == 14.4

    micros[0].send_message('out', Message(0.0, None, 'testing back'))
    msg = macros[0].receive_message('in')
    assert msg.data == 'testing back'
    assert macros[0].get_parameter_value('test2') == 14.4

    # test receive_with_parameters
    qmc.send_message('parameters_out', Message(0.0, None, config0), 1)

    assert macros[1].reuse_instance()
    macros[1].send_message('out', Message(0.0, 1.0, 'testing'))
    assert micros[1].reuse_instance(False)
    msg = micros[1].receive_message_with_parameters('in')
    assert msg.data == 'testing'
    assert msg.configuration['test2'] == 14.4
    assert micros[1].get_parameter_value('test2') == 13.3

    # test receive_with_parameters incorrect reuse_instance
    qmc.send_message('parameters_out', Message(0.0, None, config0), 2)

    assert macros[2].reuse_instance()
    macros[2].send_message('out', Message(0.0, 1.0, 'testing'))
    assert micros[2].reuse_instance()
    with pytest.raises(RuntimeError):
        micros[2].receive_message_with_parameters('in')
