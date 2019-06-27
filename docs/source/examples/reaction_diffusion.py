from collections import OrderedDict
import logging

from matplotlib import pyplot as plt
import numpy as np

from libmuscle import Instance, Message
from libmuscle.runner import run_simulation
from ymmsl import (ComputeElement, Conduit, Configuration, Model, Operator,
                   Settings)


def reaction() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # list of float
            Operator.O_F: ['final_state']})         # list of float

    while instance.reuse_instance():
        # f_init
        t_max = instance.get_parameter_value('t_max', 'float')
        dt = instance.get_parameter_value('dt', 'float')
        k = instance.get_parameter_value('k', 'float')

        msg = instance.receive('initial_state')
        U = np.array(msg.data)

        t_cur = msg.timestamp
        while t_cur + dt < t_max:
            # O_i

            # S
            U += k * U * dt
            t_cur += dt

        # O_f
        instance.send('final_state', Message(t_cur, None, U.tolist()))


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
    instance = Instance({
            Operator.O_I: ['state_out'],
            Operator.S: ['state_in']})

    while instance.reuse_instance():
        # f_init
        t_max = instance.get_parameter_value('t_max', 'float')
        dt = instance.get_parameter_value('dt', 'float')
        x_max = instance.get_parameter_value('x_max', 'float')
        dx = instance.get_parameter_value('dx', 'float')
        d = instance.get_parameter_value('d', 'float')

        U = np.zeros(int(round(x_max / dx)))
        U[25] = 2.0
        U[50] = 2.0
        U[75] = 2.0
        Us = U

        t_cur = 0.0
        while t_cur + dt <= t_max:
            # O_i
            t_next = t_cur + dt
            if t_next + dt > t_max:
                t_next = None
            cur_state_msg = Message(t_cur, t_next, U.tolist())
            instance.send('state_out', cur_state_msg)

            # S
            msg = instance.receive('state_in', default=cur_state_msg)
            if msg.timestamp > t_cur + dt:
                logging.warning('Received a message from the future!')
            U = np.array(msg.data)

            dU = np.zeros_like(U)
            dU[1:-1] = d * laplacian(U, dx) * dt
            dU[0] = dU[1]
            dU[-1] = dU[-2]

            U += dU
            Us = np.vstack((Us, U))
            t_cur += dt

        plt.figure()
        plt.imshow(np.log(Us + 1e-20))
        plt.show()


if __name__ == '__main__':
    elements = [
            ComputeElement('macro', 'diffusion'),
            ComputeElement('micro', 'reaction')]

    conduits = [
            Conduit('macro.state_out', 'micro.initial_state'),
            Conduit('micro.final_state', 'macro.state_in')]

    model = Model('reaction_diffusion', elements, conduits)
    settings = Settings(OrderedDict([
                ('micro.t_max', 2.469136e-6),
                ('micro.dt', 2.469136e-8),
                ('macro.t_max', 1.234568e-4),
                ('macro.dt', 2.469136e-6),
                ('x_max', 1.01),
                ('dx', 0.01),
                ('k', -4.05e4),     # reaction parameter
                ('d', 4.05e-2)      # diffusion parameter
                ]))

    configuration = Configuration(model, settings)

    implementations = {'diffusion': diffusion, 'reaction': reaction}
    run_simulation(configuration, implementations)
