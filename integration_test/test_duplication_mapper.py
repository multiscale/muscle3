from ymmsl import (Component, Conduit, Configuration, Operator, Model,
                   Settings)

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation


def duplication_mapper():
    """Duplication mapper implementation.
    """
    instance = Instance()

    while instance.reuse_instance():
        # o_f
        out_ports = instance.list_ports()[Operator.O_F]

        message = Message(0.0, None, 'testing')
        for out_port in out_ports:
            instance.send(out_port, message)


def receiver():
    """Receiver for messages from dm.
    """
    instance = Instance({Operator.F_INIT: ['in']})

    while instance.reuse_instance():
        # f_init
        msg = instance.receive('in')
        assert msg.data == 'testing'


def test_duplication_mapper(log_file_in_tmpdir):
    """A positive all-up test of duplication mappers.

    This is an acyclic workflow.
    """
    elements = [
            Component('dm', 'muscle.duplication_mapper'),
            Component('first', 'receiver'),
            Component('second', 'receiver')]

    conduits = [
                Conduit('dm.out', 'first.in'),
                Conduit('dm.out2', 'second.in')]

    model = Model('test_model', elements, conduits)
    settings = Settings()

    configuration = Configuration(model, settings)

    implementations = {
            'muscle.duplication_mapper': duplication_mapper,
            'receiver': receiver}
    run_simulation(configuration, implementations)
