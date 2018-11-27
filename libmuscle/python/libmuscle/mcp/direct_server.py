from typing import Dict
import uuid

from ymmsl import Reference

from libmuscle.outbox import Outbox
from libmuscle.mcp.message import Message
from libmuscle.mcp.server import Server


# indexed by server UUID
registered_servers = dict()  # type: Dict[str, Server]


class DirectServer(Server):
    """A server that server within this program

    This server is for connecting compute elements within the same
    program.
    """
    def __init__(self, outboxes: Dict[Reference, Outbox]) -> None:
        """Create a DirectServer.

        Args:
            outboxes: A dictionary of outboxes, indexed by receiver.
        """
        super().__init__(outboxes)

        self.__id = str(uuid.uuid4())
        registered_servers[self.__id] = self

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        return 'direct:{}'.format(self.__id)

    def request(self, receiver: Reference) -> Message:
        """Gets the next message for this receiver from its outbox.

        This will block until a message is available.

        Args:
            receiver: The receiver requesting the next message.

        Returns:
            The next message.
        """
        return self._outboxes[receiver].retrieve()
