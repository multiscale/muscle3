from typing import cast, Dict, List

from ymmsl import Conduit, Identifier, Reference

from libmuscle.endpoint import Endpoint


class PeerManager:
    """Manages information about peers for a Communicator
    """
    def __init__(self, kernel: Reference, index: List[int],
                 conduits: List[Conduit],
                 peer_dims: Dict[Reference, List[int]],
                 peer_locations: Dict[Reference, List[str]]) -> None:
        """Create a PeerManager.

        Peers here are instances, and peer_dims and peer_locations are
        indexed by a Reference to an instance. Instance sets are
        multi-dimensional arrays with sizes given by peer_dims.

        Args:
            kernel: The kernel for the instance whose peers we're
                    managing.
            index: The index of the instance whose peers we're
                    managing.
            conduits: A list of conduits attached to this compute
                    element, as received from the manager.
            peer_dims: For each peer we share a conduit with, the
                    dimensions of the instance set.
            peer_locations: A list of locations for each peer instance
                    we share a conduit with.
        """
        self.__kernel = kernel
        self.__index = index

        # peer port ids, indexed by local kernel.port id
        self.__peers = dict()  # type: Dict[Reference, Reference]

        for conduit in conduits:
            if str(conduit.sending_component()) == str(kernel):
                # we send on the port this conduit attaches to
                self.__peers[conduit.sender] = conduit.receiver
            if str(conduit.receiving_component()) == str(kernel):
                # we receive on the port this conduit attaches to
                self.__peers[conduit.receiver] = conduit.sender

        self.__peer_dims = peer_dims    # indexed by kernel id
        self.__peer_locations = peer_locations  # indexed by instance id

    def is_connected(self, port: Identifier) -> bool:
        """Determine whether the given port is connected.

        Args:
            port: The port to check.
        """
        recv_port_full = self.__kernel + port
        return recv_port_full in self.__peers

    def get_peer_port(self, port: Identifier) -> Reference:
        """Get a reference for the peer port.

        Args:
            port: Name of the port on this side.
        """
        return self.__peers[self.__kernel + port]

    def get_peer_dims(self, peer_kernel: Reference) -> List[int]:
        """Get the dimensions of a peer kernel.

        Args:
            peer_kernel: The peer kernel whose dimensions to get.
        """
        return self.__peer_dims[peer_kernel]

    def get_peer_locations(self, peer_instance: Reference) -> List[str]:
        """Get the locations of a peer instance.

        There may be multiple, if the peer supports more than one
                protocol.

        Args:
            peer_instance: The instance whose locations to get.
        """
        return self.__peer_locations[peer_instance]

    def get_peer_endpoint(self, port: Identifier, slot: List[int]
                          ) -> Endpoint:
        """Determine the peer endpoint for the given port and slot.

        Args:
            port: The port on our side to send or receive on.
            slot: The slot to send or receive on.

        Returns:
            The peer endpoint.
        """
        peer = self.__peers[self.__kernel + port]
        peer_kernel = cast(Reference, peer[:-1])
        peer_port = cast(Identifier, peer[-1])

        total_index = self.__index + slot

        # rebalance the indices
        peer_dim = len(self.__peer_dims[peer_kernel])
        peer_index = total_index[0:peer_dim]
        peer_slot = total_index[peer_dim:]
        return Endpoint(peer_kernel, peer_index, peer_port, peer_slot)
