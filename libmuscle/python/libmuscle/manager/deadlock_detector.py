import logging
from threading import Thread
import time
from typing import Callable, Dict, List, Optional, Tuple
from queue import Empty, Queue


_logger = logging.getLogger(__name__)
_QueueItem = Tuple[bool, str, str, str, Optional[int]]


class DeadlockDetector(Thread):
    """The DeadlockDetector attempts to detect when multiple instances are stuck waiting
    for each other.

    This class is responsible for handling WAITING_FOR_RECEIVE and
    WAITING_FOR_RECEIVE_DONE MMP messages, which are submitted by the MMPServer.

    When a deadlock is detected, the cycle of instances that is waiting on each other is
    logged with FATAL severity. If this deadlock does not get resoled in
    ``wait_before_shutdown`` seconds, the simulation is shut down.
    """

    def __init__(
            self, shutdown_callback: Callable[[], None], wait_before_shutdown: float
            ) -> None:
        """Construct a new DeadlockDetector thread.

        Args:
            shutdown_callback: function to execute when a deadlock is detected. This
                callback (which is executed in this thread!) is responsible for stopping
                the simulation when a deadlock is detected.
            wait_before_shutdown: Number of seconds to wait before executing
                :param:`shutdown_callback` after a deadlock is detected. If the deadlock
                is resolved (although this is unlikely), the simulation will not shut
                down.
        """
        super().__init__(name="DeadlockDetector")

        self._shutdown_callback = shutdown_callback
        self._wait_before_shutdown = wait_before_shutdown

        self._queue: Queue[Optional[_QueueItem]] = Queue()
        """Queue of incoming messages. Incoming messages can come in any communication
        thread and will be consumed and processed in this worker thread.
        """
        self._waiting_instances: Dict[str, str] = {}
        """Maps instance IDs to the peer instance IDs they are waiting for."""
        self._waiting_instance_ports: Dict[str, Tuple[str, Optional[int]]] = {}
        """Maps instance IDs to the port/slot they are waiting on.."""

        self._detected_deadlocks: List[List[str]] = []
        """List of deadlocked instance cycles. Set by _handle_potential_deadlock.
        """
        self._shutdown_time: Optional[float] = None
        """Future time when we confirm the potential deadlock and abort the simulation.
        """

    def run(self) -> None:
        """Logic that is executed in the thread."""
        while True:
            # Set a timeout when a deadlock was detected
            seconds_until_abort = None
            if self._shutdown_time is not None:
                seconds_until_abort = max(0, self._shutdown_time - time.monotonic())

            # Grab a new item from the queue, this raises Empty when timeout expires:
            try:
                item = self._queue.get(timeout=seconds_until_abort)
                if item is None:  # On shutdown, None is pushed to the queue
                    return  # exit thread
                self._process_queue_item(item)

            except Empty:
                # Timeout was set and has expired without any new messages:
                # - We only set a timeout when there is a deadlock
                # - An item is pushed to the queue when any instance sends a
                #   WAITING_FOR_RECEIVE_DONE message (which may cancel a potential
                #   deadlock)
                # Therefore:
                # - We have not received a message cancelling a deadlock cycle
                #   (otherwise this would have triggered a _process_queue_item, clearing
                #   self._shutdown_time and we had not set another timeout). And so a
                #   deadlock is still present. Assert it to be absolutely certain:
                assert self._detected_deadlocks
                formatted_deadlocks = "\n\n".join(
                        self._format_deadlock(instances)
                        for instances in self._detected_deadlocks)
                _logger.fatal(
                        "Aborting simulation: deadlock detected.\n%s",
                        formatted_deadlocks)
                self._shutdown_callback()
                return

    def shutdown(self) -> None:
        """Stop the deadlock detector thread."""
        self._queue.put(None)

    def put_waiting(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Queue a WAITING_FOR_RECEIVE message from an instance for processing.

        This method can be called from any thread.

        Args:
            instance_id: ID of instance that is waiting to receive a message.
            peer_instance_id: ID of the peer that the instance is waiting on.
            port_name: Name of the input port.
            slot: Optional slot number of the input port.
        """
        self._queue.put((True, instance_id, peer_instance_id, port_name, slot))

    def put_waiting_done(
            self, instance_id: str, peer_instance_id: str,
            port_name: str, slot: Optional[int]
            ) -> None:
        """Queue a WAITING_FOR_RECEIVE_DONE message from an instance for processing.

        This method can be called from any thread.

        Args:
            instance_id: ID of instance that is waiting to receive a message.
            peer_instance_id: ID of the peer that the instance is waiting on.
            port_name: Name of the input port.
            slot: Optional slot number of the input port.
        """
        self._queue.put((False, instance_id, peer_instance_id, port_name, slot))

    def _process_queue_item(self, item: _QueueItem) -> None:
        """Actually process a WAITING_FOR_RECEIVE[_DONE] request.

        This method should be called inside the worker thread.
        """
        _logger.debug("Processing queue item: %s", item)
        is_waiting, instance_id, peer_instance_id, port_name, slot = item
        if is_waiting:
            # Sanity checks, triggering this is a bug in the instance or the manager
            assert instance_id not in self._waiting_instances

            # Register that the instance is waiting
            self._waiting_instances[instance_id] = peer_instance_id
            self._waiting_instance_ports[instance_id] = (port_name, slot)
            self._check_for_deadlock(instance_id)

        else:
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
            if not self._detected_deadlocks:
                # There are no deadlocks anymore: cancel shutdown
                if self._shutdown_time is not None:
                    _logger.info("Deadlock has resolved, abort is cancelled.")
                    self._shutdown_time = None

    def _check_for_deadlock(self, instance_id: str) -> None:
        """Check if there is a cycle of waiting instances that involves this instance.
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

        Args:
            deadlock_instances: list of instances waiting on eachother
        """
        shutdown_delay = self._wait_before_shutdown
        if self._shutdown_time is not None:
            # Get time until shutdown
            shutdown_delay = self._shutdown_time - time.monotonic()
        _logger.fatal(
                "Potential deadlock detected, aborting run in %d seconds.\n%s",
                shutdown_delay,
                self._format_deadlock(deadlock_instances),
                )

        self._detected_deadlocks.append(deadlock_instances)
        if self._shutdown_time is None:
            self._shutdown_time = time.monotonic() + self._wait_before_shutdown

    def _format_deadlock(self, deadlock_instances: List[str]) -> str:
        """Create and return formatted deadlock debug info.

        Args:
            deadlock_instances: list of instances waiting on eachother
        """
        num_instances = str(len(deadlock_instances))
        lines = [f"The following {num_instances} instances are deadlocked:"]
        for i, instance in enumerate(deadlock_instances):
            num = str(i+1).rjust(len(num_instances))
            peer_instance = self._waiting_instances[instance]
            port, slot = self._waiting_instance_ports[instance]
            slot_txt = "" if slot is None else f"[{slot}]"
            lines.append(
                f"{num}. Instance '{instance}' is waiting on instance '{peer_instance}'"
                f" in a receive on port '{port}{slot_txt}'."
            )
        return "\n".join(lines)
