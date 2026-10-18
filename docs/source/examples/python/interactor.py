import logging

from ymmsl.v0_2 import Operator

from libmuscle import Instance, Message

logger = logging.getLogger("program")


def interactor() -> None:
    instance = Instance(
        {Operator.O_I: ["data_out"], Operator.S: ["data_in"]},
    )

    while instance.reuse_instance():
        # f_init
        t_start = instance.get_setting("t_start", "float")
        dt = instance.get_setting("dt", "float")
        t_end = instance.get_setting("t_end", "float")

        t_cur = t_start
        while t_cur < t_end:
            t_next = t_cur + dt
            logger.debug("t_cur = %s, t_next = %s", t_cur, t_next)

            # o_i
            t_next_sent = t_next if t_next < t_end else None
            instance.send("data_out", Message(t_cur, t_next_sent, t_cur))

            # s
            msg = instance.receive("data_in")
            logger.debug("Received data %s at %s", msg.data, msg.timestamp)

            t_cur = t_next


if __name__ == "__main__":
    logging.basicConfig()
    interactor()
