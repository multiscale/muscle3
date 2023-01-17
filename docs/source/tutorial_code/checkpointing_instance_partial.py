"""MUSCLE3 Python component template.

Note that this template is not executable as is, please have a look at the
examples in ``docs/source/examples`` to see working components."""

from libmuscle import Instance, Message, USES_CHECKPOINT_API
from ymmsl import Operator

instance = Instance({
        Operator.F_INIT: ["F_INIT_Port"],
        Operator.O_I: ["O_I_Port"],
        Operator.S: ["S_Port"],
        Operator.O_F: ["O_F_Port"]}, USES_CHECKPOINT_API)

while instance.reuse_instance():
    # F_INIT
    setting = instance.get_setting("setting")
    ...

    instance.receive("F_INIT_Port")
    ...

    while t_cur <= t_max:
        # O_I
        t_next = t + dt
        if t_next > t_max:
            t_next = None

        instance.send("O_I_Port", Message(t_cur, t_next, data))
        ...

        # S
        instance.receive("S_Port")
        ...

        t_cur += dt

        if instance.should_save_snapshot(t_cur):
            state = ...  # component implementation
            msg = Message(t_cur, data=state)
            instance.save_snapshot(msg)

    # O_F
    instance.send("O_F_Port", Message(t_cur, data=data))

    if instance.should_save_final_snapshot():
        state = ...  # component implementation
        msg = Message(t_cur, data=state)
        instance.save_final_snapshot(msg)
