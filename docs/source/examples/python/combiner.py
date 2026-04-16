import logging
from ymmsl import Operator
from libmuscle import Instance, InstanceFlags, Message


def main():
    # 1. Request dynamic port configuration by not providing a ports description
    instance = Instance()
    # Optionally provide instance flags with: Instance(flags=...)

    while instance.reuse_instance():
        # 2. Request which ports are available:
        ports = instance.list_ports()
        # check that we don't have any O_I or S ports defined
        if ports.get(Operator.O_I) or ports.get(Operator.S):
            msg = "The combiner component does not support O_I or S ports."
            instance.error_shutdown(msg)
            raise RuntimeError(msg)

        # 3. Receive on all connected F_INIT ports
        input_messages = []
        for port in sorted(ports.get(Operator.F_INIT, [])):
            if instance.is_connected(port):
                input_messages.append(instance.receive(port))

        # Check that we at least one input
        if not input_messages:
            msg = "The combiner actor requires at least one connected F_INIT port."
            instance.error_shutdown(msg)
            raise RuntimeError(msg)

        # 4. Combine the input and send on connected O_F ports
        timestamp = input_messages[0].timestamp
        next_timestamp = input_messages[0].next_timestamp
        data = [msg.data for msg in input_messages]
        output = Message(timestamp, next_timestamp, data)

        for port in ports.get(Operator.O_F, []):
            instance.send(port, output)


if __name__ == "__main__":
    logging.basicConfig()
    main()
