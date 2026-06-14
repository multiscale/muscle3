from typing import cast

from ymmsl.v0_2 import Conduit, Identifier, Reference, Port

from libmuscle.endpoint import Endpoint


class PeerInfo:
    """Interprets information about peers for a Communicator
    """
    def __init__(self, kernel: Reference, index: list[int],
                 conduits: list[Conduit],
                 peer_dims: dict[Reference, list[int]],
                 peer_locations: dict[Reference, list[str]],
                 ymmsl_ports: list[Port]) -> None:
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
            ymmsl_ports: Port declaration for this component from the yMMSL
                    configuration.
        """
        self._kernel = kernel
        self._index = index
        self._conduits = conduits

        self._incoming_ports: list[Reference] = []
        self._outgoing_ports: list[Reference] = []

        # peer port ids, indexed by local kernel.port id
        self._peers: dict[Reference, list[Reference]] = {}

        for conduit in conduits:
            if str(conduit.sending_component()) == str(kernel):
                # we send on the port this conduit attaches to
                if conduit.sender not in self._outgoing_ports:
                    self._outgoing_ports.append(conduit.sender)
                self._peers.setdefault(conduit.sender, []).append(
                        conduit.receiver)

            if str(conduit.receiving_component()) == str(kernel):
                # we receive on the port this conduit attaches to
                if conduit.receiver in self._peers:
                    raise RuntimeError(
                            f'Receiving port "{conduit.receiving_port()}" is connected'
                            ' by multiple conduits, but at most one is allowed.')
                self._incoming_ports.append(conduit.receiver)
                self._peers[conduit.receiver] = [conduit.sender]

        self._peer_dims = peer_dims    # indexed by kernel id
        self._peer_locations = peer_locations  # indexed by instance id
        self._ymmsl_ports = ymmsl_ports

    def list_ymmsl_ports(self) -> list[Port]:
        """list ports declared in the yMMSL configuration"""
        return self._ymmsl_ports

    def list_incoming_ports(self) -> list[tuple[Identifier, Reference]]:
        """list incoming ports.

        Returns:
            A list of tuples containing a port id and a reference to the
            peer endpoint.
        """
        return [
                (cast(Identifier, port_ref[-1]), self._peers[port_ref][0])
                for port_ref in self._incoming_ports]

    def list_outgoing_ports(self) -> list[tuple[Identifier, list[Reference]]]:
        """list outgoing ports.

        Returns:
            A list of tuples containing a port id and a list of references
            to the peer endpoint(s).
        """
        return [
                (cast(Identifier, port_ref[-1]), self._peers[port_ref])
                for port_ref in self._outgoing_ports]

    def is_connected(self, port: Identifier) -> bool:
        """Determine whether the given port is connected.

        Args:
            port: The port to check.
        """
        recv_port_full = self._kernel + port
        return recv_port_full in self._peers

    def get_peer_ports(self, port: Identifier) -> list[Reference]:
        """Get a reference for the peer ports.

        Args:
            port: Name of the port on this side.
        """
        return self._peers[self._kernel + port]

    def get_peer_dims(self, peer_kernel: Reference) -> list[int]:
        """Get the dimensions of a peer kernel.

        Args:
            peer_kernel: The peer kernel whose dimensions to get.
        """
        return self._peer_dims[peer_kernel]

    def get_peer_locations(self, peer_instance: Reference) -> list[str]:
        """Get the locations of a peer instance.

        There may be multiple, if the peer supports more than one
                protocol.

        Args:
            peer_instance: The instance whose locations to get.
        """
        return self._peer_locations[peer_instance]

    def get_peer_endpoints(self, port: Identifier, slot: list[int]
                           ) -> list[Endpoint]:
        """Determine the peer endpoints for the given port and slot.

        Args:
            port: The port on our side to send or receive on.
            slot: The slot to send or receive on.

        Returns:
            The peer endpoints.
        """
        peers = self._peers[self._kernel + port]
        endpoints = []

        for peer in peers:
            peer_kernel = peer[:-1]
            peer_port = cast(Identifier, peer[-1])

            total_index = self._index + slot

            # rebalance the indices
            peer_dim = len(self._peer_dims[peer_kernel])
            peer_index = total_index[0:peer_dim]
            peer_slot = total_index[peer_dim:]
            endpoints.append(
                    Endpoint(peer_kernel, peer_index, peer_port, peer_slot))

        return endpoints

    def check_peer_dimensions(self, port_id: Identifier) -> list[int]:
        """Checks peer dimensions are as expected.

        Args:
            port_id: Port to check peer dimensions for.

        Returns:
            Dimensions of connected peers.
        """
        if not self.is_connected(port_id):
            return []
        peer_ports = self.get_peer_ports(port_id)
        peer_port = peer_ports[0]
        peer_component = peer_port[:-1]
        port_peer_dims = self.get_peer_dims(peer_component)
        for peer_port in peer_ports[1:]:
            peer_component = peer_port[:-1]
            if port_peer_dims != self.get_peer_dims(peer_component):
                port_strs = ", ".join(map(str, peer_ports))
                raise RuntimeError(
                    f'Multicast port "{port_id}" is connected to peers with'
                    " different dimensions. All peer components that"
                    " this port is connected to must have the same"
                    f" multiplicity. Connected to ports: {port_strs}."
                )
        return port_peer_dims
