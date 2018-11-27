from typing import Dict

from ymmsl import Reference

from libmuscle.outbox import Outbox


class Server:
    """A server that accepts MCP connections.

    This is a base class for MCP Servers. An MCP Server accepts
    connections over some lower-level communication protocol, and
    processes message requests by sending the requested message.
    """
    def __init__(self, outboxes: Dict[Reference, Outbox]) -> None:
        """Create a Server.

        Args:
            outboxes: A dictionary of outboxes, indexed by receiver.
        """
        self._outboxes = outboxes

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        raise NotImplementedError()  # pragma: no cover
