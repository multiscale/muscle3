import logging
import time

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation
from ymmsl.v0_2 import (
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
                'component1', Ports(o_f=['out']), 'First component', 'buffer'),
            Component(
                'component2', Ports(f_init=['in'], o_f=['out']), 'Second component',
                'buffer'),
            Component(
                'component3', Ports(f_init=['in']), 'Third component', 'buffer')]

    conduits = [
            Conduit('component1.out', 'component2.in'),
            Conduit('component2.out', 'component3.in')]

    model = Model(
            'dispatch', description='A model demonstrating dispatch between three'
            ' components', components=components, conduits=conduits)
    settings = Settings({})
    configuration = Configuration(models=[model], settings=settings)

    implementations = {'buffer': buffer}
    run_simulation(configuration, implementations)
