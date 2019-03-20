from typing import List

import pytest
from ymmsl import Operator, Reference

from libmuscle.communicator import Message
from libmuscle.compute_element import ComputeElement
from libmuscle.muscle3 import run_instances, Muscle3


def duplication_mapper(instance_id: str):
    """Duplication mapper implementation.
    """
    muscle = Muscle3()
    ce = ComputeElement(instance_id)
    muscle.register(ce)

    while ce.reuse_instance():
        # o_f
        out_ports = ce.list_ports()[Operator.O_F]

        message = Message(0.0, None, 'testing')
        for out_port in out_ports:
            ce.send_message(out_port, message)
    muscle.close()


def receiver(instance_id: str):
    """Receiver for messages from dm.
    """
    muscle = Muscle3()
    ce = ComputeElement(instance_id, {Operator.F_INIT: ['in']})
    muscle.register(ce)

    while ce.reuse_instance():
        # f_init
        msg = ce.receive_message('in')
        assert msg.data == 'testing'
    muscle.close()


def test_duplication_mapper(mmp_server_dm, sys_argv_manager):
    """A positive all-up test of duplication mappers.

    This is an acyclic workflow.
    """
    submodels = {
            'dm': duplication_mapper,
            'first': receiver,
            'second': receiver}
    run_instances(submodels)
