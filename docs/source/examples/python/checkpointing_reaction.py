import logging

from libmuscle import Grid, Instance, Message, USES_CHECKPOINT_API
from ymmsl import Operator


def reaction() -> None:
    """A simple exponential reaction model on a 1D grid.
    """
    instance = Instance({
            Operator.F_INIT: ['initial_state'],     # 1D Grid
            Operator.O_F: ['final_state']},         # 1D Grid
            USES_CHECKPOINT_API)

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
