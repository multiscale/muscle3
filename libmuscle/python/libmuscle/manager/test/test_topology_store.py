from ymmsl.v0_2 import Reference


def test_create_topology_store(topology_store) -> None:
    assert topology_store.model.conduits[0].sender == 'macro.out'
    assert topology_store.model.conduits[0].receiver == 'micro.in'
    assert topology_store.model.conduits[1].sender == 'micro.out'
    assert topology_store.model.conduits[1].receiver == 'macro.in'

    assert topology_store.model.components['macro'].multiplicity == []
    assert topology_store.model.components['micro'].multiplicity == [10, 10]


def test_get_conduits(topology_store2) -> None:
    conduits = topology_store2.get_conduits(Reference('macro'))
    assert conduits[0].sender == 'macro.out'
    assert conduits[0].receiver == 'meso.init'
    assert conduits[1].sender == 'meso.final'
    assert conduits[1].receiver == 'macro.in'

    conduits = topology_store2.get_conduits(Reference('meso'))
    assert conduits[0].sender == 'macro.out'
    assert conduits[0].receiver == 'meso.init'
    assert conduits[1].sender == 'meso.out'
    assert conduits[1].receiver == 'micro.init'
    assert conduits[2].sender == 'micro.final'
    assert conduits[2].receiver == 'meso.in'
    assert conduits[3].sender == 'meso.final'
    assert conduits[3].receiver == 'macro.in'


def test_get_peer_dimensions(topology_store) -> None:
    macro_peer_dims = topology_store.get_peer_dimensions(Reference('macro'))

    assert len(macro_peer_dims) == 1
    assert Reference('micro') in macro_peer_dims
    assert macro_peer_dims[Reference('micro')] == [10, 10]

    micro_peer_dims = topology_store.get_peer_dimensions(Reference('micro'))

    assert len(micro_peer_dims) == 1
    assert Reference('macro') in micro_peer_dims
    assert micro_peer_dims[Reference('macro')] == []
