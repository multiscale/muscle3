import logging
import os
import socket

from libmuscle import Instance, Message
from ymmsl import Operator


def log_location() -> None:
    """Log where we are running so that the test can check for it."""
    print(socket.gethostname())
    print(','.join(map(str, sorted(os.sched_getaffinity(0)))))


def component() -> None:
    """A simple dummy component.

    This sends and receives on all operators, allowing different coupling patterns
    with a single program.
    """
    instance = Instance({
            Operator.F_INIT: ['init_in'],
            Operator.O_I: ['inter_out'],
            Operator.S: ['inter_in'],
            Operator.O_F: ['final_out']})

    while instance.reuse_instance():
        # F_INIT
        steps = instance.get_setting('steps', 'int')

        instance.receive('init_in', default=Message(0.0))

        for step in range(steps):
            # O_I
            instance.send('inter_out', Message(step))

            # S
            instance.receive('inter_in', default=Message(0.0))

        # O_F
        instance.send('final_out', Message(steps))


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    log_location()
    component()
