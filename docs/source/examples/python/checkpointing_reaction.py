import logging

from libmuscle import Grid, Instance, Message
from ymmsl import Operator


def reaction() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # list of float
            Operator.O_F: ['final_state']})         # list of float

    while instance.reuse_instance():
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        k = instance.get_setting('k', 'float')

        if instance.resuming():
            msg = instance.load_snapshot()
            if msg.data is not None:
                # A final snapshot does not have data in it, but that's fine: we
                # will do the F_INIT step inside `should_init()` below.
                U = msg.data[0].array.copy()
                t_cur = msg.timestamp
                t_stop = msg.data[1]

        # F_INIT
        if instance.should_init():
            msg = instance.receive('initial_state')
            U = msg.data.array.copy()
            t_cur = msg.timestamp
            t_stop = msg.timestamp + t_max

        while t_cur + dt < t_stop:
            # O_I

            # S
            U += k * U * dt
            t_cur += dt

            if instance.should_save_snapshot(t_cur):
                instance.save_snapshot(Message(t_cur, None, [
                        Grid(U, ['x']),
                        t_stop]))

        # O_F
        instance.send('final_state', Message(t_cur, None, Grid(U, ['x'])))

        if instance.should_save_final_snapshot():
            instance.save_final_snapshot(Message(t_cur, None, None))


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    reaction()
