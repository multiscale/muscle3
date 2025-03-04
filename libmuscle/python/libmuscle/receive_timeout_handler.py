from typing import Optional

from ymmsl import Reference

from libmuscle.mcp.transport_client import TimeoutHandler
from libmuscle.mmp_client import MMPClient


class Deadlock(Exception):
    """Exception that is raised when the simulation has deadlocked."""


class ReceiveTimeoutHandler(TimeoutHandler):
    """Timeout handler when receiving messages from peers.

    This handler sends a message to the Muscle Manager when the receive times out (and
    another message when the message does arrive).

    This is used by the manager to detect if the simulation is in a deadlock, where a
    cycle of instances is waiting for each other.
    """

    def __init__(
            self, manager: MMPClient,
            peer_instance: Reference, port_name: str, slot: Optional[int],
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
        # Counter to keep track of the number of timeouts
        self._num_timeouts = 0

    @property
    def timeout(self) -> float:
        # Increase timeout by a factor 1.5 with every timeout we hit:
        factor = 1.5 ** self._num_timeouts
        return self._timeout * factor

    def on_timeout(self) -> None:
        if self._num_timeouts == 0:
            # Notify the manager that we're waiting for a receive
            self._manager.waiting_for_receive(
                    self._peer_instance, self._port_name, self._slot)
        else:
            # Ask the manager if we're part of a detected deadlock
            if self._manager.is_deadlocked():
                raise Deadlock()
        self._num_timeouts += 1

    def on_receive(self) -> None:
        self._manager.waiting_for_receive_done(
                self._peer_instance, self._port_name, self._slot)
