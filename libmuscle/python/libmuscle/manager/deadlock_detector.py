import logging
from threading import Lock
from typing import Dict, List, Optional, Tuple


_logger = logging.getLogger(__name__)


class DeadlockDetector:
    """The DeadlockDetector attempts to detect when multiple instances are stuck waiting
    for each other.

    This class is responsible for handling WAITING_FOR_RECEIVE, IS_DEADLOCKED and
    WAITING_FOR_RECEIVE_DONE MMP messages, which are submitted by the MMPServer.

    When a deadlock is detected, the cycle of instances that is waiting for each other
    is logged with FATAL severity.
    """

    def __init__(self) -> None:
        """Construct a new DeadlockDetector."""
        self._mutex = Lock()
        """Mutex that should be locked before accessing instance variables."""
        self._waiting_instances: Dict[str, str] = {}
        """Maps instance IDs to the peer instance IDs they are waiting for."""
        self._waiting_instance_ports: Dict[str, Tuple[str, Optional[int]]] = {}
        """Maps instance IDs to the port/slot they are waiting for.."""
        self._detected_deadlocks: List[List[str]] = []
        """List of deadlocked instance cycles. Set by _handle_potential_deadlock."""

    def waiting_for_receive(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Process a WAITING_FOR_RECEIVE message from an instance.

        This method can be called from any thread.

        Args:
            instance_id: ID of instance that is waiting to receive a message.
            peer_instance_id: ID of the peer that the instance is waiting for.
            port_name: Name of the input port.
            slot: Optional slot number of the input port.
        """
        with self._mutex:
            # Sanity checks, triggering this is a bug in the instance or the manager
            assert instance_id not in self._waiting_instances

            # Register that the instance is waiting
            self._waiting_instances[instance_id] = peer_instance_id
            self._waiting_instance_ports[instance_id] = (port_name, slot)
            self._check_for_deadlock(instance_id)

    def waiting_for_receive_done(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Process a WAITING_FOR_RECEIVE_DONE message from an instance.

        This method can be called from any thread.

        Args:
            instance_id: ID of instance that is waiting to receive a message.
            peer_instance_id: ID of the peer that the instance is waiting for.
            port_name: Name of the input port.
            slot: Optional slot number of the input port.
        """
        with self._mutex:
            # Sanity checks, triggering these is a bug in the instance or the manager
            assert instance_id in self._waiting_instances
            assert self._waiting_instances[instance_id] == peer_instance_id
            assert self._waiting_instance_ports[instance_id] == (port_name, slot)

            # We're not waiting anymore
            del self._waiting_instances[instance_id]
            del self._waiting_instance_ports[instance_id]

            # Check if we were part of a deadlock
            for i, instance_list in enumerate(self._detected_deadlocks):
                if instance_id in instance_list:
                    del self._detected_deadlocks[i]
                    break

    def is_deadlocked(self, instance_id: str) -> bool:
        """Check if the provided instance is part of a detected deadlock.

        This method can be called from any thread.
        """
        with self._mutex:
            for deadlock_instances in self._detected_deadlocks:
                if instance_id in deadlock_instances:
                    _logger.fatal(
                            "Deadlock detected, simulation is aborting!\n%s",
                            self._format_deadlock(deadlock_instances))
                    return True
        return False

    def _check_for_deadlock(self, instance_id: str) -> None:
        """Check if there is a cycle of waiting instances that involves this instance.

        Make sure to lock self._mutex before calling this.
        """
        deadlock_instances = [instance_id]
        cur_instance = instance_id
        while cur_instance in self._waiting_instances:
            cur_instance = self._waiting_instances[cur_instance]
            if cur_instance == instance_id:
                self._handle_potential_deadlock(deadlock_instances)
                return
            deadlock_instances.append(cur_instance)
        _logger.debug("No deadlock detected")

    def _handle_potential_deadlock(self, deadlock_instances: List[str]) -> None:
        """Handle a potential deadlock.

        Make sure to lock self._mutex before calling this.

        Args:
            deadlock_instances: list of instances waiting for eachother
        """
        self._detected_deadlocks.append(deadlock_instances)

    def _format_deadlock(self, deadlock_instances: List[str]) -> str:
        """Create and return formatted deadlock debug info.

        Args:
            deadlock_instances: list of instances waiting for eachother
        """
        num_instances = str(len(deadlock_instances))
        lines = [f"The following {num_instances} instances are deadlocked:"]
        for i, instance in enumerate(deadlock_instances):
            num = str(i+1).rjust(len(num_instances))
            peer_instance = self._waiting_instances[instance]
            port, slot = self._waiting_instance_ports[instance]
            slot_txt = "" if slot is None else f"[{slot}]"
            lines.append(
                f"{num}. Instance '{instance}' is waiting for instance"
                f" '{peer_instance}' in a receive on port '{port}{slot_txt}'."
            )
        return "\n".join(lines)
