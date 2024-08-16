from typing import Optional

from libmuscle.mcp.transport_client import TimeoutHandler
from libmuscle.mmp_client import MMPClient


class ReceiveTimeoutHandler(TimeoutHandler):
    """Timeout handler when receiving messages from peers.

    This handler sends a message to the Muscle Manager when the receive times out (and
    another message when the message does arrive).

    This is used by the manager to detect if the simulation is in a deadlock, where a
    cycle of instances is waiting on each other.
    """

    def __init__(
            self, manager: MMPClient,
            peer_instance: str, port_name: str, slot: Optional[int],
            timeout: float
            ) -> None:
        """Initialize a new timeout handler.

        Args:
            manager: Connection to the muscle manager.
            peer_instance: the peer instance we try to receive from.
            port_name: the name of the port we try to receive on.
            slot: the slot we try to receive on.
            timeout: Timeout in seconds.
        """
        self._manager = manager
        self._peer_instance = peer_instance
        self._port_name = port_name
        self._slot = slot
        self._timeout = timeout

    @property
    def timeout(self) -> float:
        return self._timeout

    def on_timeout(self) -> None:
        self._manager.waiting_for_receive(
                self._peer_instance, self._port_name, self._slot)

    def on_receive(self) -> None:
        self._manager.waiting_for_receive_done(
                self._peer_instance, self._port_name, self._slot)
