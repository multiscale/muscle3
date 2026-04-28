"""Source and destination components to test the combiner component"""
import logging

import sys

from ymmsl import Operator
from libmuscle import Instance, InstanceFlags, Message


def source():
    print("Starting source component")
    instance = Instance({Operator.O_F: ["data"]})

    while instance.reuse_instance():
        data = instance.get_setting("data")
        instance.send("data", Message(0.0, data=data))


def destination():
    print("Starting destination component")
    instance = Instance({Operator.F_INIT: ["input"]})

    while instance.reuse_instance():
        msg = instance.receive("input")
        # Test expected messages that we received
        assert msg.timestamp == 0.0
        assert isinstance(msg.data, list)
        for i in range(len(msg.data)):
            # source1 will send 1, source2 will send 2, etc.
            assert msg.data[i] == i + 1, msg.data


if __name__ == "__main__":
    logging.basicConfig()
    if sys.argv[-1] == "source":
        source()
    elif sys.argv[-1] == "destination":
        destination()
    else:
        raise RuntimeError("Was expecting source or destination as argument")
