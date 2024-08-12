import logging
from threading import Thread
from typing import Callable, Dict, List, Optional, Tuple
from queue import Queue


_logger = logging.getLogger(__name__)
_QueueItem = Tuple[bool, str, str, str, Optional[int]]


class DeadlockDetector(Thread):
    """TODO"""

    def __init__(
            self, shutdown_callback: Callable[[], None], wait_before_shutdown: float
            ) -> None:
        super().__init__(name="DeadlockDetector")

        self._shutdown_callback = shutdown_callback
        self._wait_before_shutdown = wait_before_shutdown

        self._queue: Queue[Optional[_QueueItem]] = Queue()
        self._waiting_instances: Dict[str, str] = {}
        self._waiting_instance_ports: Dict[str, Tuple[str, int]] = {}

        self._detected_deadlocks: List[str] = []

    def run(self) -> None:
        """Logic that is executed in the thread."""
        while True:
            item = self._queue.get()
            if item is None:  # Shutdown sentinal
                return
            # Handle item
            self._process_queue_item(item)

    def shutdown(self) -> None:
        """Stop the deadlock detector thread."""
        self._queue.put(None)

    def put_waiting(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Process a WATING_FOR_RECEIVE message from an instance."""
        self._queue.put((True, instance_id, peer_instance_id, port_name, slot))

    def put_waiting_done(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Process a WATING_FOR_RECEIVE_DONE message from an instance."""
        self._queue.put((False, instance_id, peer_instance_id, port_name, slot))

    def _process_queue_item(self, item: _QueueItem) -> None:
        _logger.info("Processing queue item: %s", item)
        is_waiting, instance_id, peer_instance_id, port_name, slot = item
        if is_waiting:
            # Sanity checks, triggering this is a bug in the instance or the manager
            if instance_id in self._waiting_instances:
                _logger.error(
                    "Instance %s was already waiting on a receive call. "
                    "Did we miss a WAITING DONE event?",
                    instance_id)
            # Register that the instance is waiting
            self._waiting_instances[instance_id] = peer_instance_id
            self._waiting_instance_ports[instance_id] = (port_name, slot)
            self._check_for_deadlock(instance_id)

        else:
            # Sanity checks, triggering these is a bug in the instance or the manager
            if instance_id not in self._waiting_instances:
                _logger.error(
                    "Instance %s is not waiting on a receive call.", instance_id)
            elif self._waiting_instances[instance_id] != peer_instance_id:
                _logger.error(
                    "Instance %s was waiting for %s, not for %s.",
                    instance_id,
                    self._waiting_instances[instance_id],
                    peer_instance_id)
            elif self._waiting_instance_ports[instance_id] != (port_name, slot):
                _logger.error(
                    "Instance %s was waiting on port[slot] %s[%s], not on %s[%s]",
                    instance_id,
                    *self._waiting_instance_ports[instance_id],
                    port_name, slot)
            else:
                del self._waiting_instances[instance_id]
                del self._waiting_instance_ports[instance_id]

    def _check_for_deadlock(self, instance_id: str) -> None:
        """Check if there is a cycle of waiting instances that involves this instance.
        """
        deadlock_instances = [instance_id]
        cur_instance = instance_id
        while cur_instance in self._waiting_instances:
            cur_instance = self._waiting_instances[cur_instance]
            if cur_instance == instance_id:
                break  # Found a deadlocked cycle
            deadlock_instances.append(cur_instance)
        else:  # No cycle detected
            _logger.info("No deadlock detected")
            return

        _logger.warning(
            "Potential deadlock detected, aborting run in %d seconds.\n%s",
            self._wait_before_shutdown,
            self._format_deadlock(deadlock_instances),
            )
        # TODO: wait and abort
        self._shutdown_callback()

    def _format_deadlock(self, instances: List[str]) -> str:
        """Create and return formatted deadlock debug info."""
        num_instances = str(len(instances))
        lines = [f"The following {num_instances} instances are dead-locked:"]
        for i, instance in enumerate(instances):
            num = str(i+1).rjust(len(num_instances))
            peer_instance = self._waiting_instances[instance]
            port, slot = self._waiting_instance_ports[instance]
            slot_txt = "" if slot is None else f"[{slot}]"
            lines.append(
                f"{num}. Instance '{instance}' is waiting on instance '{peer_instance}'"
                f" in a receive on port '{port}{slot_txt}'."
            )
        return "\n".join(lines)
