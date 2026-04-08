import os
from typing import Optional
from libmuscle import Instance, Message
from ymmsl.v0_2 import Configuration, Operator, Reference


class ImplementationTester:
    """
    The ImplementationTester creates a MUSCLE3 Instance that acts as the
    "tester" component, which is connected to the implementation under test.
    """

    def __init__(self, default_timeout: float, muscle_manager_address: str,
                 test_ymmsl_config: Configuration) -> None:
        """
        Initialize the implementation tester.

        Args:
            default_timeout: Default timeout for receive operations in seconds.
        """
        self._default_timeout = default_timeout
        # Pass manager address and instance name through environment
        os.environ["MUSCLE_MANAGER"] = muscle_manager_address
        os.environ["MUSCLE_INSTANCE"] = "muscle3_implementation_tester"
        test_model = test_ymmsl_config.models[Reference("muscle3_test_model")]
        tester_component = test_model.components[
            Reference("muscle3_implementation_tester")]
        instance_ports = {
            Operator.O_I: [str(p) for p in tester_component.ports.sending_port_names()],
            Operator.S: [str(p) for p in tester_component.ports.receiving_port_names()]
        }
        self._instance = Instance(ports=instance_ports)
        self._instance.reuse_instance()

    def send(
        self, port_name: str, message: Message, slot: Optional[int] = None
    ) -> None:
        """
        Send a message on the specified port.

        Args:
            port_name: Name of the port to send on (without 'send_' prefix).
            message: The message to send.
            slot: Optional slot number for vector ports.
        """
        self._instance.send(port_name, message, slot)

    def receive(
        self,
        port_name: str,
        slot: Optional[int] = None,
        *,
        timeout: Optional[float] = None,
    ) -> Message:
        """
        Receive a message from the specified port.

        Args:
            port_name: Name of the port to receive from (without 'receive_' prefix).
            slot: Optional slot number for vector ports.
            timeout: Timeout in seconds. If None, uses default_timeout.
        """
        # TODO: Should implement what should be done when we reached the timeout
        if timeout is None:
            timeout = self._default_timeout

        return self._instance.receive(port_name, slot)

    def cleanup(self) -> None:
        while self._instance.reuse_instance():
            pass
