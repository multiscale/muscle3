from ymmsl import (Component, Conduit, Configuration, Operator, Model,
                   Settings)

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation


def multicaster():
    instance = Instance({Operator.O_F: ['out']})

    while instance.reuse_instance():
        # o_f
        message = Message(0.0, data='testing')
        instance.send('out', message)


def receiver():
    instance = Instance({Operator.F_INIT: ['in']})

    while instance.reuse_instance():
        # f_init
        msg = instance.receive('in')
        assert msg.data == 'testing'


def test_multicast(log_file_in_tmpdir):
    elements = [
            Component('broadcast', 'broadcaster'),
            Component('first', 'receiver'),
            Component('second', 'receiver')]

    conduits = [
                Conduit('broadcast.out', 'first.in'),
                Conduit('broadcast.out', 'second.in')]

    model = Model('test_model', elements, conduits)
    settings = Settings()

    configuration = Configuration(model, settings)

    implementations = {
            'broadcaster': multicaster,
            'receiver': receiver}
    run_simulation(configuration, implementations)
