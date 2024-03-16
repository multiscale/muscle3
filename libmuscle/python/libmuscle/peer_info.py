from typing import cast, Dict, List, Tuple

from ymmsl import Conduit, Identifier, Reference

from libmuscle.endpoint import Endpoint


class PeerInfo:
    """Interprets information about peers for a Communicator
    """
    def __init__(self, kernel: Reference, index: List[int],
                 conduits: List[Conduit],
                 peer_dims: Dict[Reference, List[int]],
                 peer_locations: Dict[Reference, List[str]]) -> None:
        """Create a PeerInfo.

        Peers here are instances, and peer_dims and peer_locations are
        indexed by a Reference to an instance. Instance sets are
        multi-dimensional arrays with sizes given by peer_dims.

        Args:
            kernel: The kernel for the instance whose peers we're
                    managing.
            index: The index of the instance whose peers we're
                    managing.
            conduits: A list of conduits attached to this component,
                    as received from the manager.
            peer_dims: For each peer we share a conduit with, the
                    dimensions of the instance set.
            peer_locations: A list of locations for each peer instance
                    we share a conduit with.
        """
        self.__kernel = kernel
        self.__index = index

        self._incoming_ports: List[Reference] = []
        self._outgoing_ports: List[Reference] = []

        # peer port ids, indexed by local kernel.port id
        self.__peers: Dict[Reference, List[Reference]] = {}

        for conduit in conduits:
            if str(conduit.sending_component()) == str(kernel):
                # we send on the port this conduit attaches to
                if conduit.sender not in self._outgoing_ports:
                    self._outgoing_ports.append(conduit.sender)
                self.__peers.setdefault(conduit.sender, []).append(
                        conduit.receiver)

            if str(conduit.receiving_component()) == str(kernel):
                # we receive on the port this conduit attaches to
                if conduit.receiver in self.__peers:
                    raise RuntimeError(('Receiving port "{}" is connected by'
                                        ' multiple conduits, but at most one'
                                        ' is allowed.'
                                        ).format(conduit.receiving_port()))
                self._incoming_ports.append(conduit.receiver)
                self.__peers[conduit.receiver] = [conduit.sender]

        self.__peer_dims = peer_dims    # indexed by kernel id
        self.__peer_locations = peer_locations  # indexed by instance id

    def list_incoming_ports(self) -> List[Tuple[Identifier, Reference]]:
        """List incoming ports.

        Returns:
            A list of tuples containing a port id and a reference to the
            peer endpoint.
        """
        return [
                (cast(Identifier, port_ref[-1]), self.__peers[port_ref][0])
                for port_ref in self._incoming_ports]

    def list_outgoing_ports(self) -> List[Tuple[Identifier, List[Reference]]]:
        """List outgoing ports.

        Returns:
            A list of tuples containing a port id and a list of references
            to the peer endpoint(s).
        """
        return [
                (cast(Identifier, port_ref[-1]), self.__peers[port_ref])
                for port_ref in self._outgoing_ports]

    def is_connected(self, port: Identifier) -> bool:
        """Determine whether the given port is connected.

        Args:
            port: The port to check.
        """
        recv_port_full = self.__kernel + port
        return recv_port_full in self.__peers

    def get_peer_ports(self, port: Identifier) -> List[Reference]:
        """Get a reference for the peer ports.

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

    def get_peer_endpoints(self, port: Identifier, slot: List[int]
                           ) -> List[Endpoint]:
        """Determine the peer endpoints for the given port and slot.

        Args:
            port: The port on our side to send or receive on.
            slot: The slot to send or receive on.

        Returns:
            The peer endpoints.
        """
        peers = self.__peers[self.__kernel + port]
        endpoints = []

        for peer in peers:
            peer_kernel = peer[:-1]
            peer_port = cast(Identifier, peer[-1])

            total_index = self.__index + slot

            # rebalance the indices
            peer_dim = len(self.__peer_dims[peer_kernel])
            peer_index = total_index[0:peer_dim]
            peer_slot = total_index[peer_dim:]
            endpoints.append(
                    Endpoint(peer_kernel, peer_index, peer_port, peer_slot))

        return endpoints
