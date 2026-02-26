from libmuscle import Instance, Message
from ymmsl import Operator

import sys
import time


def driver():
    instance = Instance({
        Operator.O_I: ['out'],
        Operator.S: ['in']})

    # Message size is base_size * scale_base**scale, with scale in
    # the range [0..num_scales).
    base_size = instance.get_setting('base_size', 'int')
    scale_base = instance.get_setting('scale_base', 'int')
    num_scales = instance.get_setting('num_scales', 'int')
    num_repeats = instance.get_setting('num_repeats', 'int')

    # in seconds
    pre_send_delay = instance.get_setting('pre_send_delay', 'float')
    pre_recv_delay = instance.get_setting('pre_recv_delay', 'float')

    while instance.reuse_instance():
        # wait a bit to make sure mirror is running
        time.sleep(0.2)

        for scale in range(num_scales):
            size = base_size * scale_base**scale
            if size > 10 * 1024**3:
                raise RuntimeError('Messages >10GB are not supported')

            message = bytes(size)
            for _ in range(num_repeats):
                time.sleep(pre_send_delay)
                instance.send('out', Message(0.0, None, message))

                time.sleep(pre_recv_delay)
                msg = instance.receive('in')


def mirror():
    instance = Instance({
        Operator.O_I: ['out'],
        Operator.S: ['in']})

    num_scales = instance.get_setting('num_scales', 'int')
    num_repeats = instance.get_setting('num_repeats', 'int')

    # in seconds
    pre_send_delay = instance.get_setting('pre_send_delay', 'float')
    pre_recv_delay = instance.get_setting('pre_recv_delay', 'float')

    while instance.reuse_instance():
        for scale in range(num_scales):
            for _ in range(num_repeats):
                time.sleep(pre_recv_delay)
                msg = instance.receive('in')

                time.sleep(pre_send_delay)
                instance.send('out', msg)


if __name__ == '__main__':
    if len(sys.argv) < 2 or sys.argv[1] not in ('driver', 'mirror'):
        raise RuntimeError(
                'Please specify "driver" or "mirror" as the first argument')
    if sys.argv[1] == 'driver':
        driver()
    else:
        mirror()
