from libmuscle import Instance, Message
from ymmsl import Operator


instance = Instance({
        Operator.F_INIT: ['init'],
        Operator.O_F: ['final']})

while instance.reuse_instance():
    # f_init
    msg = instance.receive('init')

    # o_f
    instance.send('final', Message(msg.timestamp, msg.next_timestamp, msg.data))
