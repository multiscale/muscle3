from ymmsl import Operator

from libmuscle import Instance, Message

instance = Instance(
    {
        Operator.F_INIT: ["init"],
        Operator.O_I: ["out", "out1"],
        Operator.S: ["in", "in1"],
        Operator.O_F: ["final"],
    }
)

while instance.reuse_instance():
    # f_init
    msg = instance.receive("init")
    x = msg.data
    total = 0

    # default timeline: o_i, then s
    for i in range(2):
        instance.send("out", Message(msg.timestamp + i, None, x + i))
        total += instance.receive("in").data

    # timeline sub1: s, then o_i
    for i in range(2):
        y = instance.receive("in1").data
        total += y
        instance.send("out1", Message(msg.timestamp + i, None, x + y))

    # o_f
    instance.send("final", Message(msg.timestamp, None, total))
