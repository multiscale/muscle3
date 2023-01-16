import logging

from libmuscle import Grid, Instance, Message, USES_CHECKPOINT_API
from ymmsl import Operator


def reaction() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # list of float
            Operator.O_F: ['final_state']},         # list of float
            USES_CHECKPOINT_API)

    while instance.reuse_instance():
        # F_INIT
        t_max = instance.get_setting('t_max', 'float')
        dt = instance.get_setting('dt', 'float')
        k = instance.get_setting('k', 'float')

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
                msg = Message(t_cur, data=[Grid(U, ['x']), t_stop])
                instance.save_snapshot(msg)

        # O_F
        instance.send('final_state', Message(t_cur, data=Grid(U, ['x'])))

        if instance.should_save_final_snapshot():
            msg = Message(t_cur)
            instance.save_final_snapshot(msg)


if __name__ == '__main__':
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)
    reaction()
