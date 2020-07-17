from queue import Queue


class Outbox:
    """Stores messages to be sent to a particular receiver.

    An Outbox is a queue of messages, which may be deposited and
    then retrieved in the same order.
    """
    def __init__(self) -> None:
        """Create an empty Outbox.
        """
        self.__queue = Queue()  # type: Queue[bytes]

    def is_empty(self) -> bool:
        """Returns True iff the outbox is empty.
        """
        return self.__queue.empty()

    def deposit(self, message: bytes) -> None:
        """Put a message in the Outbox.

        The message will be placed at the back of a queue, and may be
        retrieved later via :py:meth:`retrieve`.

        Args:
            message: The message to store.
        """
        self.__queue.put(message)

    def retrieve(self) -> bytes:
        """Retrieve a message from the Outbox.

        The message will be removed from the front of the queue, and
        returned to the caller. Blocks if the queue is empty, until a
        message is deposited.

        Returns:
            The next message.
        """
        return self.__queue.get()
