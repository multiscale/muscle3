import logging
import numpy as np

from libmuscle import Grid, Instance, Message
from ymmsl import Operator


def reaction() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # list of float
            Operator.O_F: ['final_state']})         # list of float

    while instance.reuse_instance():
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        k = instance.get_setting('k', 'float')

        msg = instance.receive('initial_state')
        U = msg.data.array.copy()

        t_cur = msg.timestamp
        while t_cur + dt < msg.timestamp + t_max:
            # O_I

            # S
            U += k * U * dt
            t_cur += dt

        # O_F
        instance.send('final_state', Message(t_cur, None, Grid(U, ['x'])))


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    reaction()
