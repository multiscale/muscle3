from typing import List

import pytest
from ymmsl import (ComputeElementDecl, Conduit, Experiment, Operator,
                   Reference, Simulation, YmmslDocument)

from libmuscle.communicator import Message
from libmuscle.instance import Instance
from muscle_manager.muscle_manager import run_simulation


def duplication_mapper(instance_id: str):
    """Duplication mapper implementation.
    """
    instance = Instance(instance_id)

    while instance.reuse_instance():
        # o_f
        out_ports = instance.list_ports()[Operator.O_F]

        message = Message(0.0, None, 'testing')
        for out_port in out_ports:
            instance.send_message(out_port, message)


def receiver(instance_id: str):
    """Receiver for messages from dm.
    """
    instance = Instance(instance_id, {Operator.F_INIT: ['in']})

    while instance.reuse_instance():
        # f_init
        msg = instance.receive_message('in')
        assert msg.data == 'testing'


def test_duplication_mapper(log_file_in_tmpdir):
    """A positive all-up test of duplication mappers.

    This is an acyclic workflow.
    """
    elements = [
            ComputeElementDecl('dm', 'muscle.duplication_mapper'),
            ComputeElementDecl('first', 'receiver'),
            ComputeElementDecl('second', 'receiver')]

    conduits = [
                Conduit('dm.out', 'first.in'),
                Conduit('dm.out2', 'second.in')]

    simulation = Simulation('test_model', elements, conduits)
    settings = Experiment('test_model', [])

    experiment = YmmslDocument('v0.1', settings, simulation)

    submodels = {
            'dm': duplication_mapper,
            'first': receiver,
            'second': receiver}
    run_simulation(experiment, submodels)
