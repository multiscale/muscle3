from typing import List

from ymmsl import Reference
from libmuscle.mcp.message import Message


class Outbox:
    """Stores messages to be sent to a particular receiver.

    An Outbox is a queue of messages, which may be deposited and
    then retrieved in the same order.
    """
    def __init__(self) -> None:
        """Create an empty Outbox.
        """
        self.__queue = list()  # type: List[Message]

    def deposit(self, message: Message) -> None:
        """Put a message in the Outbox.

        The message will be placed at the back of a queue, and may be
        retrieved later via :py:meth:`retrieve`.

        Args:
            message: The message to store.
        """
        self.__queue.insert(0, message)
        # TODO: signal that we have a message

    def retrieve(self) -> Message:
        """Retrieve a message from the Outbox.

        The message will be removed from the front of the queue, and
        returned to the caller.

        Returns:
            The next message.
        """
        # TODO: wait for a message to arrive
        return self.__queue.pop()
