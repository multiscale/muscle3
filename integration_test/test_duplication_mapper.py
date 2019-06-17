from typing import List

import pytest
from ymmsl import (ComputeElement, Conduit, Configuration, Operator, Reference,
                   Model, Settings)

from libmuscle.communicator import Message
from libmuscle.instance import Instance
from muscle_manager.muscle_manager import run_simulation


def duplication_mapper():
    """Duplication mapper implementation.
    """
    instance = Instance()

    while instance.reuse_instance():
        # o_f
        out_ports = instance.list_ports()[Operator.O_F]

        message = Message(0.0, None, 'testing')
        for out_port in out_ports:
            instance.send_message(out_port, message)


def receiver():
    """Receiver for messages from dm.
    """
    instance = Instance({Operator.F_INIT: ['in']})

    while instance.reuse_instance():
        # f_init
        msg = instance.receive_message('in')
        assert msg.data == 'testing'


def test_duplication_mapper(log_file_in_tmpdir):
    """A positive all-up test of duplication mappers.

    This is an acyclic workflow.
    """
    elements = [
            ComputeElement('dm', 'muscle.duplication_mapper'),
            ComputeElement('first', 'receiver'),
            ComputeElement('second', 'receiver')]

    conduits = [
                Conduit('dm.out', 'first.in'),
                Conduit('dm.out2', 'second.in')]

    model = Model('test_model', elements, conduits)
    settings = Settings()

    configuration = Configuration('v0.1', model, settings)

    implementations = {
            'muscle.duplication_mapper': duplication_mapper,
            'receiver': receiver}
    run_simulation(configuration, implementations)
