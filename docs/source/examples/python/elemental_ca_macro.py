import logging
import os

import numpy as np

from libmuscle import Grid, Instance, Message
from ymmsl import Operator


def elemental_ca_macro() -> None:
    """A simple elementary cellular automata on a 1d grid.

    This model tries to solve an elemental ca, the actual calculation of the
    next timestap is delegated to the micro model. The macro model only
    collects the results
    """
    logger = logging.getLogger()
    instance = Instance({
            Operator.O_I: ['state_out'],
            Operator.S: ['state_in'],
            Operator.O_F: ['final_state_out']})

    while instance.reuse_instance():
        # F_INIT
        max_steps = instance.get_setting('max_steps', 'int')
        size = instance.get_setting('size', 'int')

        U = np.random.choice(a=[False, True], size=(size,))
        Us = U

        for step in range(max_steps):
            # O_I
            cur_state_msg = Message(step, data=Grid(U, ['x']))
            instance.send('state_out', cur_state_msg)

            # S
            msg = instance.receive('state_in')
            np.copyto(U, msg.data.array)

            Us = np.vstack((Us, U))

        # O_F
        final_state_msg = Message(step, data=Grid(U, ['x']))
        instance.send('final_state_out', final_state_msg)

        if 'DONTPLOT' not in os.environ and 'SLURM_NODENAME' not in os.environ:
            from matplotlib import pyplot as plt
            plt.figure()
            plt.imshow(
                    Us,
                    origin='upper',
                    #extent=[
                    #    -0.5*dx, x_max - 0.5*dx,
                    #    (t_max - 0.5*dt) * 1000.0, -0.5*dt * 1000.0],
                    interpolation='none',
                    aspect='auto'
                    )
            #cbar = plt.colorbar()
            #cbar.set_label('log(Concentration)', rotation=270, labelpad=20)
            plt.xlabel('x')
            plt.ylabel('t (steps)')
            plt.title('Evolution over time')
            plt.show()


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    elemental_ca_macro()
