from typing import Dict, List, Optional, Tuple

from ymmsl import Identifier, Operator

from libmuscle.peer_info import PeerInfo
from libmuscle.port import Port


class PortManager:
    """Manages sending and receiving ports of the current instance."""
    def __init__(
            self, index: List[int], declared_ports: Optional[Dict[Operator, List[str]]]
            ) -> None:
        """Create a PortManager.

        Args:
            index: The index of this instance.
            declared_ports: The ports this instance has, as declared by the
                    user when creating the Instance object.
        """
        self._index = index
        self._ports: Dict[str, Port] = {}
        self._declared_ports = declared_ports

    def connect_ports(self, peer_info: PeerInfo) -> None:
        """Connect the ports to their peers.

        This is the second stage in the simulation wiring process.

        Peers here are instances, and the information about them received
        from the manager is in peer_info. We are going to create a set of
        Port objects here, one for each of our ports.

        If the user gave us a set of ports (i.e. they were declared in the
        code) then we'll create a Port object for each of those, with
        information about the attached conduit / peer (if any) from
        peer_info. If the user did not give us any ports (which is legal),
        then the ports will be created entirely from the information
        received from the manager.  The user then has to use
        Instance.list_ports() to see what ports they got, and do something
        with them.

        Args:
            peer_info: Information about our peers from the manager.
        """
        self._muscle_settings_in = self._settings_in_port(peer_info)
        if self._declared_ports:
            self._ports = self._ports_from_declared(peer_info)
        else:
            self._ports = self._ports_from_conduits(peer_info)

    def settings_in_connected(self) -> bool:
        """Returns whether muscle_settings_in is connected."""
        return self._muscle_settings_in.is_connected()

    def list_ports(self) -> Dict[Operator, List[str]]:
        """Returns a description of the ports this PortManager has.

        Returns:
            A dictionary, indexed by Operator, containing lists of
            port names. Operators with no associated ports are not
            included.
        """
        result: Dict[Operator, List[str]] = {}
        for port_name, port in self._ports.items():
            if port.operator not in result:
                result[port.operator] = list()
            result[port.operator].append(port_name)
        return result

    def port_exists(self, port_name: str) -> bool:
        """Returns whether a port with the given name exists.

        Args:
            port_name: Port name to check.

        Returns:
            True iff the port exists
        """
        return port_name in self._ports

    def get_port(self, port_name: str) -> Port:
        """Returns a Port object describing a port with the given name.

        Args:
            port_name: Name of the port to retrieve.

        Returns:
            A Port object for the port
        """
        return self._ports[port_name]

    def restore_message_counts(
            self, port_message_counts: Dict[str, List[int]]) -> None:
        """Restore message counts on all ports.

        Args:
            port_message_counts: The message counts, as a dictionary indexed by
                    port name containing a list of counts, one for each slot.
        """
        for port_name, num_messages in port_message_counts.items():
            if port_name == "muscle_settings_in":
                self._muscle_settings_in.restore_message_counts(num_messages)
            elif port_name in self._ports:
                self._ports[port_name].restore_message_counts(num_messages)
            else:
                raise RuntimeError(f'Unknown port {port_name} in snapshot.'
                                   ' Have your port definitions changed since'
                                   ' the snapshot was taken?')

    def get_message_counts(self) -> Dict[str, List[int]]:
        """Get message counts for all ports on the communicator.

        Returns:
            A dictionary indexed by port name containing a list of counts, one
            for each slot of the corresponding port.
        """
        port_message_counts = {port_name: port.get_message_counts()
                               for port_name, port in self._ports.items()}
        port_message_counts["muscle_settings_in"] = \
            self._muscle_settings_in.get_message_counts()
        return port_message_counts

    def _settings_in_port(self, peer_info: PeerInfo) -> Port:
        """Creates a Port representing muscle_settings_in.

        Args:
            peer_info: Information about our peers from the manager.
        """
        msi = Identifier('muscle_settings_in')
        if peer_info.is_connected(msi):
            sender_component = peer_info.get_peer_ports(msi)[0][:-1]
            return Port(
                    str(msi), Operator.F_INIT, False, True, len(self._index),
                    peer_info.get_peer_dims(sender_component))

        return Port(
                str(msi), Operator.F_INIT, False, False, len(self._index), [])

    def _ports_from_declared(self, peer_info: PeerInfo) -> Dict[str, Port]:
        """Derives port definitions from supplied declaration.

        Args:
            peer_info: Information about our peers from the manager.

        Returns:
            A dictionary keyed by port name containing corresponding Port
                    objects.
        """
        assert self._declared_ports is not None

        ports = dict()
        for operator, port_list in self._declared_ports.items():
            for port_desc in port_list:
                port_name, is_vector = self._split_port_desc(port_desc)
                if port_name.startswith('muscle_'):
                    raise RuntimeError(
                            'Port names starting with "muscle_" are reserved for'
                            ' MUSCLE, please rename port "{}"'.format(port_name))
                port_id = Identifier(port_name)
                is_connected = peer_info.is_connected(port_id)
                if is_connected:
                    peer_ports = peer_info.get_peer_ports(port_id)
                    peer_port = peer_ports[0]
                    peer_component = peer_port[:-1]
                    port_peer_dims = peer_info.get_peer_dims(peer_component)
                    for peer_port in peer_ports[1:]:
                        peer_component = peer_port[:-1]
                        if port_peer_dims != peer_info.get_peer_dims(peer_component):
                            port_strs = ', '.join(map(str, peer_ports))
                            raise RuntimeError(
                                    'Multicast port "{}" is connected to peers with'
                                    ' different dimensions. All peer components that'
                                    ' this port is connected to must have the same'
                                    ' multiplicity. Connected to ports: {}.'.format(
                                        port_name, port_strs))
                else:
                    port_peer_dims = []
                ports[port_name] = Port(
                        port_name, operator, is_vector, is_connected,
                        len(self._index), port_peer_dims)
        return ports

    def _ports_from_conduits(self, peer_info: PeerInfo) -> Dict[str, Port]:
        """Derives port definitions from conduits.

        Args:
            peer_info: Information about our peers from the manager.
        """
        ports = dict()

        def make_port(
                port_id: Identifier, operator: Operator, peer_dims: List[int]) -> None:
            if not str(port_id).startswith('muscle_'):
                ndims = max(0, len(peer_dims) - len(self._index))
                is_vector = (ndims == 1)
                is_connected = peer_info.is_connected(port_id)
                ports[str(port_id)] = Port(
                        str(port_id), operator, is_vector, is_connected,
                        len(self._index), peer_dims)

        for port_id, sender_ref in peer_info.list_incoming_ports():
            peer_dims = peer_info.get_peer_dims(sender_ref[:-1])
            make_port(port_id, Operator.F_INIT, peer_dims)

        for port_id, receiver_refs in peer_info.list_outgoing_ports():
            peer_dims = peer_info.get_peer_dims(receiver_refs[0][:-1])
            make_port(port_id, Operator.O_F, peer_dims)

        return ports

    def _split_port_desc(self, port_desc: str) -> Tuple[str, bool]:
        """Split a port description into its name and dimensionality.

        Expects a port description of the form port_name or
        port_name[], and returns the port name and whether it is a
        vector port.

        Args:
            port_desc: A port description string, as above.
        """
        is_vector = False
        if port_desc.endswith('[]'):
            is_vector = True
            port_desc = port_desc[:-2]

        if port_desc.endswith('[]'):
            raise ValueError(('Port description "{}" is invalid: ports can'
                              ' have at most one dimension.').format(
                                  port_desc))

        return port_desc, is_vector
