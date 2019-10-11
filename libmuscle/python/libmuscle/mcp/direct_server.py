from typing import Dict
import uuid

from ymmsl import Reference

from libmuscle.post_office import PostOffice
from libmuscle.mcp.server import Server


# indexed by server UUID
registered_servers = dict()  # type: Dict[str, Server]


class DirectServer(Server):
    """A server that server within this program

    This server is for connecting compute element instances within the
    same process.
    """
    def __init__(self, instance_id: Reference, post_office: PostOffice
                 ) -> None:
        """Create a DirectServer.

        Args:
            instance_id: Id of the instance we're a server for.
            post_office: A PostOffice to obtain messages from, for
                    servicing requests.
        """
        super().__init__(instance_id, post_office)

        self.__id = str(uuid.uuid4())
        registered_servers[self.__id] = self

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        return 'direct:{}'.format(self.__id)

    def request(self, receiver: Reference) -> bytes:
        """Gets the next message for this receiver from its outbox.

        This will block until a message is available.

        Args:
            receiver: The receiver requesting the next message.

        Returns:
            The next message.
        """
        return self._post_office.get_message(receiver)

    def close(self) -> None:
        """Closes this server.

        Since we have no network connections or other resources, this
        is a no-op.
        """
        pass
