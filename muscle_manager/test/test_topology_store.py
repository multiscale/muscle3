from muscle_manager.topology_store import TopologyStore

import pytest
from ymmsl import Reference


def test_create_topology_store(topology_store) -> None:
    assert topology_store.conduits[0].sender == 'macro.out'
    assert topology_store.conduits[0].receiver == 'micro.in'
    assert topology_store.conduits[1].sender == 'micro.out'
    assert topology_store.conduits[1].receiver == 'macro.in'

    assert topology_store.kernel_dimensions['macro'] == []
    assert topology_store.kernel_dimensions['micro'] == [10, 10]


def test_get_conduits() -> None:
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    meso:\n'
            '      implementation: meso_implementation\n'
            '      multiplicity: 10\n'
            '    micro:\n'
            '      implementation: micro_implementation\n'
            '      multiplicity: [10, 10]\n'
            '  conduits:\n'
            '    macro.state_out: meso.in\n'
            '    meso.state_out: micro.in\n'
            '    micro.final_out: meso.state_in\n'
            '    meso.out: macro.state_in\n')

    import yatiml
    import logging
    yatiml.logger.setLevel(logging.DEBUG)

    store = TopologyStore(ymmsl_text)

    conduits = store.get_conduits(Reference('macro'))
    assert conduits[0].sender == 'macro.state_out'
    assert conduits[0].receiver == 'meso.in'
    assert conduits[1].sender == 'meso.out'
    assert conduits[1].receiver == 'macro.state_in'

    conduits = store.get_conduits(Reference('meso'))
    assert conduits[0].sender == 'macro.state_out'
    assert conduits[0].receiver == 'meso.in'
    assert conduits[1].sender == 'meso.state_out'
    assert conduits[1].receiver == 'micro.in'
    assert conduits[2].sender == 'micro.final_out'
    assert conduits[2].receiver == 'meso.state_in'
    assert conduits[3].sender == 'meso.out'
    assert conduits[3].receiver == 'macro.state_in'


def test_get_peer_dimensions(topology_store) -> None:
    macro_peer_dims = topology_store.get_peer_dimensions(Reference('macro'))

    assert len(macro_peer_dims) == 1
    assert Reference('micro') in macro_peer_dims
    assert macro_peer_dims[Reference('micro')] == [10, 10]

    micro_peer_dims = topology_store.get_peer_dimensions(Reference('micro'))

    assert len(micro_peer_dims) == 1
    assert Reference('macro') in micro_peer_dims
    assert micro_peer_dims[Reference('macro')] == []


def test_data_error() -> None:
    ymmsl_text = 'version: v0.1\n'
    with pytest.raises(ValueError):
        TopologyStore(ymmsl_text)
