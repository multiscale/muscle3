import logging
import os
from typing import Optional
from libmuscle import Instance, InstanceFlags, Message
from ymmsl.v0_2 import Configuration, Operator, Reference


_logger = logging.getLogger(__name__)


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
        self._is_shut_down = False
        # Pass manager address and instance name through environment
        os.environ["MUSCLE_MANAGER"] = muscle_manager_address
        os.environ["MUSCLE_INSTANCE"] = "muscle3_implementation_tester"
        test_model = test_ymmsl_config.programs[
            Reference("muscle3_implementation_tester")
            ]
        instance_ports = {
            Operator.O_I: [str(p) for p in test_model.ports.sending_port_names()],
            Operator.S: [str(p) for p in test_model.ports.receiving_port_names()]
        }
        self._instance = Instance(
                ports=instance_ports,
                flags=InstanceFlags.SKIP_MMSF_SEQUENCE_CHECKS)
        # Configure the deadlock-detection timeout to match the default receive
        # timeout: after `default_timeout` seconds of waiting the manager is
        # notified, and if a deadlock is detected the simulation is aborted.
        self._instance._communicator.set_receive_timeout(default_timeout)
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

        Raises:
            RuntimeError: If a deadlock is detected or the connection to the
                implementation was lost while waiting for a message.
        """
        if timeout is None:
            timeout = self._default_timeout

        self._instance._communicator.set_receive_timeout(timeout)
        try:
            return self._instance.receive(port_name, slot)
        except RuntimeError as exc:
            # A RuntimeError here means either a deadlock was detected by the
            # manager, or the connection to the implementation was lost (e.g.
            # it crashed)
            _logger.error(
                "ImplementationTester: error while waiting for a message on"
                " port '%s'. Shutting down.", port_name
            )
            try:
                self._instance.error_shutdown(str(exc))
            except RuntimeError:
                self._instance.error_shutdown(str(exc), graceful=False)
            self._is_shut_down = True
            raise

    def cleanup(self) -> None:
        """Clean up the tester instance.

        Safe to call even if the instance was already shut down due to a
        timeout or deadlock error.
        """
        if not self._is_shut_down:
            while self._instance.reuse_instance():
                pass
