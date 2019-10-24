from typing import cast

from ymmsl import Reference

from libmuscle.mcp.client import Client
import libmuscle.mcp.pipe_multiplexer as mux


class PipeClient(Client):
    """A client for pipe-based communication.
    """
    @staticmethod
    def can_connect_to(location: str) -> bool:
        """Whether this client class can connect to the given location.

        Args:
            location: The location to potentially connect to.

        Returns:
            True iff this class can connect to this location.
        """
        return mux.can_connect_to(location)

    @staticmethod
    def shutdown(instance_id: Reference) -> None:
        """Free any resources shared by all clients for this instance.
        """
        if mux.can_communicate_for(instance_id):
            # close mux ends to allow clean shutdown
            mux.close_mux_ends(instance_id)
            mux_client_conn = mux.get_instance_client_conn(instance_id)
            mux_client_conn.close()

    def __init__(self, instance_id: Reference, location: str) -> None:
        """Creates a PipeClient.

        Args:
            instance_id: Our instance id.
            peer_id: Id of the peer (server) we're connecting to.
        """
        self._instance_id = instance_id

        mux_client_conn = mux.get_instance_client_conn(instance_id)
        _, peer_id = location.split('/')

        # request connection
        # This assumes that the clients are made one by one in the same thread
        # so that they can use the same pipe without getting in each other's
        # way.
        mux_client_conn.send(peer_id)
        self._conn = mux_client_conn.recv()

    def receive(self, receiver: Reference) -> bytes:
        """Receive a message from a port this client connects to.

        Args:
            receiver: The receiving (local) port.

        Returns:
            The received message.
        """
        self._conn.send(receiver)
        return cast(bytes, self._conn.recv())

    def close(self) -> None:
        """Closes this client.

        This closes any connections this client has and/or performs
        other shutdown activities.
        """
        self._conn.close()
