import logging
import os

import numpy as np

from libmuscle import Grid, Instance, Message
from ymmsl import Operator


def laplacian(Z: np.array, dx: float) -> np.array:
    """Calculates the Laplacian of vector Z.

    Args:
        Z: A vector representing a series of samples along a line.
        dx: The spacing between the samples.

    Returns:
        The second spatial derivative of Z.
    """
    Zleft = Z[:-2]
    Zright = Z[2:]
    Zcenter = Z[1:-1]
    return (Zleft + Zright - 2. * Zcenter) / dx**2


def diffusion() -> None:
    """A simple diffusion model on a 1d grid.

    The state of this model is a 1D grid of concentrations. It sends
    out the state on each timestep on `state_out`, and can receive an
    updated state on `state_in` at each state update.
    """
    logger = logging.getLogger()
    instance = Instance({
            Operator.O_I: ['state_out'],
            Operator.S: ['state_in'],
            Operator.O_F: ['final_state_out']})

    while instance.reuse_instance():
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        x_max = instance.get_setting('x_max', 'float')
        dx = instance.get_setting('dx', 'float')
        d = instance.get_setting('d', 'float')

        U = np.zeros(int(round(x_max / dx))) + 1e-20
        U[25] = 2.0
        U[50] = 2.0
        U[75] = 2.0
        Us = U

        t_cur = 0.0
        while t_cur + dt <= t_max:
            # O_I
            t_next = t_cur + dt
            if t_next + dt > t_max:
                t_next = None
            cur_state_msg = Message(t_cur, t_next, Grid(U, ['x']))
            instance.send('state_out', cur_state_msg)

            # S
            msg = instance.receive('state_in', default=cur_state_msg)
            if msg.timestamp > t_cur + dt:
                logger.warning('Received a message from the future!')
            np.copyto(U, msg.data.array)

            dU = np.zeros_like(U)
            dU[1:-1] = d * laplacian(U, dx) * dt
            dU[0] = dU[1]
            dU[-1] = dU[-2]

            U += dU
            Us = np.vstack((Us, U))
            t_cur += dt

        # O_F
        final_state_msg = Message(t_cur, None, Grid(U, ['x']))
        instance.send('final_state_out', final_state_msg)

        if 'DONTPLOT' not in os.environ and 'SLURM_NODENAME' not in os.environ:
            from matplotlib import pyplot as plt
            plt.figure()
            plt.imshow(
                    np.log(Us + 1e-20),
                    origin='upper',
                    extent=[
                        -0.5*dx, x_max - 0.5*dx,
                        (t_max - 0.5*dt) * 1000.0, -0.5*dt * 1000.0],
                    interpolation='none',
                    aspect='auto'
                    )
            cbar = plt.colorbar()
            cbar.set_label('log(Concentration)', rotation=270, labelpad=20)
            plt.xlabel('x')
            plt.ylabel('t (ms)')
            plt.title('Concentration over time')
            plt.show()


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    diffusion()
