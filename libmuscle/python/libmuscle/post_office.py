from threading import Lock
import time
from typing import Dict

from ymmsl import Reference

from libmuscle.outbox import Outbox


class PostOffice:
    """A PostOffice is an object that holds messages to be retrieved.

    A PostOffice holds outboxes with messages for receivers.
    """
    def __init__(self) -> None:
        """Create a PostOffice.
        """
        self._outboxes = dict()  # type: Dict[Reference, Outbox]

        self._outbox_lock = Lock()

    def get_message(self, receiver: Reference) -> bytes:
        """Get a message from a receiver's outbox.

        Used by servers to get messages that have been sent to another
        instance.

        Args:
            receiver: The receiver of the message.
        """
        self._ensure_outbox_exists(receiver)
        return self._outboxes[receiver].retrieve()

    def deposit(self, receiver: Reference, message: bytes) -> None:
        """Deposits a message into an outbox.

        Args:
            receiver: Receiver of the message.
            message: The message to deposit.
        """
        self._ensure_outbox_exists(receiver)
        self._outboxes[receiver].deposit(message)

    def wait_for_receivers(self) -> None:
        """Waits until all outboxes are empty.
        """
        for outbox in self._outboxes.values():
            while not outbox.is_empty():
                time.sleep(0.1)

    def _ensure_outbox_exists(self, receiver: Reference) -> None:
        """Ensure that an outbox exists.

        Outboxes are created dynamically, the first time a message is
        sent to a receiver. This function checks that an outbox exists
        for a receiver, and if not, creates one.

        Args:
            receiver: The receiver that should have an outbox.
        """
        self._outbox_lock.acquire()
        if receiver not in self._outboxes:
            self._outboxes[receiver] = Outbox()
        self._outbox_lock.release()
