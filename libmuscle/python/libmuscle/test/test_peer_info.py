import pytest

from ymmsl import Conduit, Identifier as Id, Reference as Ref

from libmuscle.peer_info import PeerInfo


@pytest.fixture
def peer_info() -> PeerInfo:
    kernel = Ref('kernel')
    index = [13]

    conduits = [
            Conduit('kernel.out', 'other.in'),
            Conduit('other.out', 'kernel.in')]

    peer_dims = {
            Ref('other'): []}

    peer_locations = {
            Ref('other'): ['tcp:other']}

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations)


@pytest.fixture
def peer_info2() -> PeerInfo:
    kernel = Ref('other')
    index = []

    conduits = [
            Conduit('kernel.out', 'other.in'),
            Conduit('other.out', 'kernel.in')]

    peer_dims = {
            Ref('kernel'): [20]}

    peer_locations = {
            Ref('kernel'): ['tcp:kernel']}

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations)


@pytest.fixture
def peer_info3() -> PeerInfo:
    kernel = Ref('kernel')
    index = []

    conduits = [
            Conduit('kernel.out', 'other.in'),
            Conduit('other.out', 'kernel.in')]

    peer_dims = {
            Ref('other'): []}

    peer_locations = {
            Ref('other'): ['tcp:other']}

    return PeerInfo(kernel, index, conduits, peer_dims, peer_locations)


def test_create_peer_info(peer_info) -> None:
    assert True


def test_is_connected(peer_info) -> None:
    assert peer_info.is_connected(Id('out'))
    assert peer_info.is_connected(Id('in'))
    assert not peer_info.is_connected(Id('not_connected'))


def test_get_peer_port(peer_info, peer_info2, peer_info3) -> None:
    assert peer_info.get_peer_ports(Id('out')) == [Ref('other.in')]
    assert peer_info.get_peer_ports(Id('in')) == [Ref('other.out')]

    assert peer_info2.get_peer_ports(Id('out')) == [Ref('kernel.in')]
    assert peer_info2.get_peer_ports(Id('in')) == [Ref('kernel.out')]

    assert peer_info3.get_peer_ports(Id('out')) == [Ref('other.in')]
    assert peer_info3.get_peer_ports(Id('in')) == [Ref('other.out')]


def test_get_peer_dims(peer_info, peer_info2, peer_info3) -> None:
    assert peer_info.get_peer_dims(Ref('other')) == []
    assert peer_info2.get_peer_dims(Ref('kernel')) == [20]
    assert peer_info3.get_peer_dims(Ref('other')) == []


def test_get_peer_locations(peer_info, peer_info2, peer_info3) -> None:
    assert peer_info.get_peer_locations(Ref('other')) == ['tcp:other']
    assert peer_info2.get_peer_locations(Ref('kernel')) == ['tcp:kernel']
    assert peer_info3.get_peer_locations(Ref('other')) == ['tcp:other']


def test_get_peer_endpoint(peer_info, peer_info2, peer_info3) -> None:
    assert str(peer_info.get_peer_endpoints(Id('out'), [])[0]) == 'other.in[13]'
    assert str(peer_info.get_peer_endpoints(Id('in'), [])[0]) == 'other.out[13]'

    assert str(peer_info2.get_peer_endpoints(Id('out'), [11])[0]) == 'kernel[11].in'
    assert str(peer_info2.get_peer_endpoints(Id('in'), [11])[0]) == 'kernel[11].out'

    assert str(peer_info3.get_peer_endpoints(Id('out'), [42])[0]) == 'other.in[42]'
    assert str(peer_info3.get_peer_endpoints(Id('in'), [42])[0]) == 'other.out[42]'
