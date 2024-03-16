from typing import List
from libmuscle.peer_info import PeerInfo
from libmuscle.port_manager import PortManager

from ymmsl import Conduit, Identifier, Operator, Reference as Ref

import pytest


@pytest.fixture
def index() -> List[int]:
    return [13]


@pytest.fixture
def port_manager(index) -> PortManager:
    declared_ports = {
            Operator.O_I: ['out'],
            Operator.S: ['in']}
    return PortManager(index, declared_ports)


@pytest.fixture
def index2() -> List[int]:
    return []


@pytest.fixture
def port_manager2(index2) -> PortManager:
    declared_ports = {
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out[]']}
    port_manager = PortManager(index2, declared_ports)

    component_id = Ref('other')
    conduits = [Conduit('component.out', 'other.in'),
                Conduit('other.out', 'component.in')]
    peer_dims = {Ref('component'): [20]}
    peer_locations = {Ref('component'): ['direct:test']}
    peer_info = PeerInfo(component_id, index2, conduits, peer_dims, peer_locations)

    port_manager.connect_ports(peer_info)
    return port_manager


def test_connect_ports(index, port_manager) -> None:
    component_id = Ref('component')
    conduits = [Conduit('component.out', 'other.in'),
                Conduit('other.settings_out', 'component.muscle_settings_in'),
                Conduit('other.out', 'component.in')]
    peer_dims = {Ref('other'): []}
    peer_locations = {Ref('other'): ['direct:test']}
    peer_info = PeerInfo(component_id, index, conduits, peer_dims, peer_locations)

    port_manager.connect_ports(peer_info)

    # check automatic ports
    assert port_manager.settings_in_connected()
    assert port_manager._muscle_settings_in.name == Identifier('muscle_settings_in')
    assert port_manager._muscle_settings_in.operator == Operator.F_INIT
    assert port_manager._muscle_settings_in._length is None

    # check declared ports
    ports = port_manager._ports
    assert ports['in'].name == Identifier('in')
    assert ports['in'].operator == Operator.S
    assert ports['in']._length is None

    assert ports['out'].name == Identifier('out')
    assert ports['out'].operator == Operator.O_I
    assert ports['out']._length is None


def test_connect_vector_ports(index) -> None:
    declared_ports = {
            Operator.F_INIT: ['in[]'],
            Operator.O_F: ['out1', 'out2[]']}

    port_manager = PortManager(index, declared_ports)

    component_id = Ref('component')
    conduits = [Conduit('other1.out', 'component.in'),
                Conduit('component.out1', 'other.in'),
                Conduit('component.out2', 'other3.in')]
    peer_dims = {
            Ref('other1'): [20, 7],
            Ref('other'): [25],
            Ref('other3'): [20]}
    peer_locations = {
            Ref('other'): ['direct:test'],
            Ref('other1'): ['direct:test1'],
            Ref('other3'): ['direct:test3']}
    peer_info = PeerInfo(component_id, index, conduits, peer_dims, peer_locations)

    port_manager.connect_ports(peer_info)

    ports = port_manager._ports
    assert ports['in'].name == Identifier('in')
    assert ports['in'].operator == Operator.F_INIT
    assert ports['in']._length == 7
    assert ports['in']._is_resizable is False

    assert ports['out1'].name == Identifier('out1')
    assert ports['out1'].operator == Operator.O_F
    assert ports['out1']._length is None

    assert ports['out2'].name == Identifier('out2')
    assert ports['out2'].operator == Operator.O_F
    assert ports['out2']._length == 0
    assert ports['out2']._is_resizable is True


def test_connect_multidimensional_ports() -> None:
    index = [13]
    declared_ports = {Operator.F_INIT: ['in[][]']}
    port_manager = PortManager(index, declared_ports)

    component_id = Ref('component')
    conduits = [Conduit(Ref('other.out'), Ref('component.in'))]
    peer_dims = {Ref('other'): [20, 7, 30]}
    peer_locations = {Ref('other'): ['direct:test']}
    peer_info = PeerInfo(component_id, index, conduits, peer_dims, peer_locations)

    with pytest.raises(ValueError):
        port_manager.connect_ports(peer_info)


def test_connect_inferred_ports() -> None:
    index = [13]
    port_manager = PortManager(index, None)

    component_id = Ref('component')
    conduits = [Conduit('other1.out', 'component.in'),
                Conduit('component.out1', 'other.in'),
                Conduit('component.out3', 'other2.in')]
    peer_dims = {
            Ref('other1'): [20, 7],
            Ref('other'): [25],
            Ref('other2'): []}
    peer_locations = {
            Ref('other'): ['direct:test'],
            Ref('other1'): ['direct:test1'],
            Ref('other2'): ['direct:test2']}
    peer_info = PeerInfo(component_id, index, conduits, peer_dims, peer_locations)

    port_manager.connect_ports(peer_info)

    ports = port_manager._ports
    assert ports['in'].name == Identifier('in')
    assert ports['in'].operator == Operator.F_INIT
    assert ports['in']._length == 7
    assert ports['in']._is_resizable is False

    assert ports['out1'].name == Identifier('out1')
    assert ports['out1'].operator == Operator.O_F
    assert ports['out1']._length is None

    assert ports['out3'].name == Identifier('out3')
    assert ports['out3'].operator == Operator.O_F
    assert ports['out3']._length is None


def test_port_message_counts(port_manager) -> None:
    port_manager.connect_ports(PeerInfo('component', [], [], {}, {}))

    msg_counts = port_manager.get_message_counts()
    assert msg_counts == {'in': [0], 'out': [0], 'muscle_settings_in': [0]}

    port_manager.get_port('in').increment_num_messages()

    msg_counts2 = port_manager.get_message_counts()
    assert msg_counts2 == {'in': [1], 'out': [0], 'muscle_settings_in': [0]}

    port_manager.get_port('out').increment_num_messages()
    port_manager.get_port('out').increment_num_messages()

    msg_counts3 = port_manager.get_message_counts()
    assert msg_counts3 == {'in': [1], 'out': [2], 'muscle_settings_in': [0]}

    port_manager._muscle_settings_in.increment_num_messages()

    msg_counts4 = port_manager.get_message_counts()
    assert msg_counts4 == {'in': [1], 'out': [2], 'muscle_settings_in': [1]}

    port_manager.restore_message_counts(msg_counts)

    msg_counts5 = port_manager.get_message_counts()
    assert msg_counts5 == {'in': [0], 'out': [0], 'muscle_settings_in': [0]}

    with pytest.raises(RuntimeError):
        port_manager.restore_message_counts({"x?invalid_port": 3})


def test_vector_port_message_counts(port_manager2) -> None:
    msg_counts = port_manager2.get_message_counts()
    assert msg_counts == {'out': [0] * 20,
                          'in': [0] * 20,
                          'muscle_settings_in': [0]}

    port_manager2.get_port('out').increment_num_messages(13)

    msg_counts = port_manager2.get_message_counts()
    assert msg_counts == {'out': [0] * 13 + [1] + [0] * 6,
                          'in': [0] * 20,
                          'muscle_settings_in': [0]}

    port_manager2.restore_message_counts({'out': list(range(20)),
                                          'in': list(range(20)),
                                          'muscle_settings_in': [4]})

    port_manager2.get_port('out').increment_num_messages(13)

    msg_counts = port_manager2.get_message_counts()
    assert msg_counts == {'out': list(range(13)) + [14] + list(range(14, 20)),
                          'in': list(range(20)),
                          'muscle_settings_in': [4]}
