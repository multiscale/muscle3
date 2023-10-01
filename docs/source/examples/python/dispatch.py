import logging
import time

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation
from ymmsl import (
        Component, Conduit, Configuration, Model, Operator, Ports, Settings)


def buffer() -> None:
    """A component that passes on its input to its output.

    If the input is not connected, it'll generate a message.
    """
    instance = Instance({
        Operator.F_INIT: ['in'],
        Operator.O_F: ['out']})

    while instance.reuse_instance():
        # F_INIT
        msg = instance.receive('in', default=Message(0.0, data='Testing'))

        # S
        time.sleep(0.25)

        # O_F
        instance.send('out', msg)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    components = [
            Component(
                'component1', 'buffer', None,
                Ports(o_f=['out'])),
            Component(
                'component2', 'buffer', None,
                Ports(f_init=['in'], o_f=['out'])),
            Component(
                'component3', 'buffer', None,
                Ports(f_init=['in']))]

    conduits = [
            Conduit('component1.out', 'component2.in'),
            Conduit('component2.out', 'component3.in')]

    model = Model('dispatch', components, conduits)
    settings = Settings({})
    configuration = Configuration(model, settings)

    implementations = {'buffer': buffer}
    run_simulation(configuration, implementations)
