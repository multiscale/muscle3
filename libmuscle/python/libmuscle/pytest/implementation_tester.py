from typing import Optional
from libmuscle import Instance, Message


class ImplementationTester:
    """
    The ImplementationTester creates a MUSCLE3 Instance that acts as the
    "tester" component, which is connected to the implementation under test.
    """

    def __init__(self, default_timeout: float) -> None:
        """
        Initialize the implementation tester.

        Args:
            default_timeout: Default timeout for receive operations in seconds.
        """
        self._default_timeout = default_timeout
        self._instance: Optional[Instance] = None
        self._initialized = False

    @property
    def _instance_checked(self) -> Instance:
        self._ensure_initialized()
        if self._instance is None:
            raise RuntimeError("MUSCLE3 Instance failed to initialize.")
        return self._instance

    def _ensure_initialized(self) -> None:
        """
        Ensure the MUSCLE3 instance is initialized.

        This creates the Instance as the 'tester' component which will
        connect to the manager and discover its ports automatically.
        """
        if not self._initialized:
            self._instance = Instance()
            self._initialized = True

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
        actual_port = f"send_{port_name}"

        if slot is not None:
            self._instance_checked.send(actual_port, message, slot)
        else:
            self._instance_checked.send(actual_port, message)

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
        actual_port = f"receive_{port_name}"

        if timeout is None:
            timeout = self._default_timeout

        if slot is not None:
            return self._instance_checked.receive(actual_port, slot)
        else:
            return self._instance_checked.receive(actual_port)
