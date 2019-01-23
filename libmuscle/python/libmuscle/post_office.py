from ymmsl import Reference

from libmuscle.mcp.message import Message


class PostOffice:
    """A PostOffice is an object that holds messages to be retrieved.

    A PostOffice holds outboxes with messages for receivers. This is
    an interface to resolve an import loop between Communicator and
    Server.
    """
    def get_message(self, receiver: Reference) -> Message:
        raise NotImplementedError()     # pragma: no cover
