from collections import OrderedDict

from matplotlib import pyplot as plt
import numpy as np
import sobol_seq

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
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        k = instance.get_setting('k', 'float')

        msg = instance.receive('initial_state')
        U = np.array(msg.data)

        t_cur = msg.timestamp
        while t_cur + dt < t_max:
            # O_I

            # S
            U += k * U * dt
            t_cur += dt

        # O_F
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
            Operator.S: ['state_in'],
            Operator.O_F: ['final_state_out']})

    while instance.reuse_instance():
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        x_max = instance.get_setting('x_max', 'float')
        dx = instance.get_setting('dx', 'float')
        d = instance.get_setting('d', 'float')

        U = np.zeros(int(round(x_max / dx)))
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
            cur_state_msg = Message(t_cur, t_next, U.tolist())
            instance.send('state_out', cur_state_msg)

            # S
            msg = instance.receive('state_in', default=cur_state_msg)
            if msg.timestamp > t_cur + dt:
                logger.warning('Received a message from the future!')
            U = np.array(msg.data)

            dU = np.zeros_like(U)
            dU[1:-1] = d * laplacian(U, dx) * dt
            dU[0] = dU[1]
            dU[-1] = dU[-2]

            U += dU
            Us = np.vstack((Us, U))
            t_cur += dt

        # O_F
        instance.send('final_state_out', Message(t_cur, None, U.tolist()))


def load_balancer() -> None:
    """A proxy which divides many calls over few instances.

    Put this component between a driver and a set of models, or between
    a macro model and a set of micro models. It will let the driver or
    macro-model submit as many calls as it wants, and divide them over
    the available (micro)model instances in a round-robin fashion.

    Assumes a fixed number of micro-model instances.

    Ports:
        front_in: Input for calls, connect to driver/macro-model O_I.
        back_out: Output to workers, connect to F_INIT of instances that
                do the work.
        back_in: Input for results, connect to O_F of instances that do
                the work.
        front_out: Output back to driver/macro-model S.
    """
    instance = Instance({
            Operator.F_INIT: ['front_in[]'],
            Operator.O_I: ['back_out[]'],
            Operator.S: ['back_in[]'],
            Operator.O_F: ['front_out[]']})

    while instance.reuse_instance(False):
        # F_INIT
        started = 0     # number started and index of next to start
        done = 0        # number done and index of next to return

        num_calls = instance.get_port_length('front_in')
        num_workers = instance.get_port_length('back_out')

        instance.set_port_length('front_out', num_calls)
        while done < num_calls:
            while started - done < num_workers and started < num_calls:
                msg = instance.receive_with_settings('front_in', started)
                instance.send('back_out', msg, started % num_workers)
                started += 1
            msg = instance.receive_with_settings('back_in', done % num_workers)
            instance.send('front_out', msg, done)
            done += 1


def qmc_driver() -> None:
    """A driver for quasi-Monte Carlo Uncertainty Quantification.

    This component attaches to a collection of model instances, and
    feeds in different parameter values generated using a Sobol
    sequence.
    """
    instance = Instance({
            Operator.O_I: ['parameters_out[]'],
            Operator.S: ['states_in[]']})

    while instance.reuse_instance():
        # F_INIT
        # get and check parameter distributions
        n_samples = instance.get_setting('n_samples', 'int')
        d_min = instance.get_setting('d_min', 'float')
        d_max = instance.get_setting('d_max', 'float')
        k_min = instance.get_setting('k_min', 'float')
        k_max = instance.get_setting('k_max', 'float')

        if d_max < d_min:
            instance.exit_error('Invalid settings: d_max < d_min')
        if k_max < k_min:
            instance.exit_error('Invalid settings: k_max < k_min')

        # generate UQ parameter values
        sobol_sqn = sobol_seq.i4_sobol_generate(2, n_samples)
        ds = d_min + sobol_sqn[:, 0] * (d_max - d_min)
        ks = k_min + sobol_sqn[:, 1] * (k_max - k_min)

        # configure output port
        if not instance.is_resizable('parameters_out'):
            instance.exit_error('This component needs a resizable'
                                ' parameters_out port, but it is connected to'
                                ' something that cannot be resized. Maybe try'
                                ' adding a load balancer.')

        instance.set_port_length('parameters_out', n_samples)

        # run ensemble
        Us = None
        # O_I
        for sample in range(n_samples):
            uq_parameters = Settings({
                'd': ds[sample],
                'k': ks[sample]})
            msg = Message(0.0, None, uq_parameters)
            instance.send('parameters_out', msg, sample)

        # S
        for sample in range(n_samples):
            msg = instance.receive_with_settings('states_in', sample)
            U = np.array(msg.data)
            # accumulate
            if Us is None:
                Us = U
            else:
                Us = np.vstack((Us, U))

        mean = np.mean(Us, axis=0)
        plt.figure()
        plt.imshow(np.log(Us + 1e-20))
        plt.show()



if __name__ == '__main__':
    elements = [
            ComputeElement('qmc', 'qmc_driver'),
            ComputeElement('rr', 'load_balancer'),
            ComputeElement('macro', 'diffusion', [10]),
            ComputeElement('micro', 'reaction', [10])]

    conduits = [
            Conduit('qmc.parameters_out', 'rr.front_in'),
            Conduit('rr.front_out', 'qmc.states_in'),
            Conduit('rr.back_out', 'macro.muscle_settings_in'),
            Conduit('macro.final_state_out', 'rr.back_in'),
            Conduit('macro.state_out', 'micro.initial_state'),
            Conduit('micro.final_state', 'macro.state_in')
            ]

    model = Model('reaction_diffusion_qmc', elements, conduits)
    settings = Settings(OrderedDict([
                ('micro.t_max', 2.469136e-6),
                ('micro.dt', 2.469136e-8),
                ('macro.t_max', 1.234568e-4),
                ('macro.dt', 2.469136e-6),
                ('x_max', 1.01),
                ('dx', 0.01),
                ('k_min', -4.455e4),
                ('k_max', -3.645e4),
                ('d_min', 0.03645),
                ('d_max', 0.04455),
                ('n_samples', 100)
                ]))

    configuration = Configuration(model, settings)

    implementations = {
            'qmc_driver': qmc_driver,
            'load_balancer': load_balancer,
            'diffusion': diffusion,
            'reaction': reaction}
    run_simulation(configuration, implementations)
