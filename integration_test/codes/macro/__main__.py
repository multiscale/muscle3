from ymmsl import Operator

from libmuscle import Instance, Message

instance = Instance({
        Operator.O_I: ['out'],
        Operator.S: ['in']})

while instance.reuse_instance():
    # f_init
    for i in range(2):
        # o_i
        instance.send('out', Message(i * 10.0, (i + 1) * 10.0, i))

        # s/b
        msg = instance.receive('in')
        assert msg.data == i
