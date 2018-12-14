from muscle_manager.topology_store import TopologyStore


def test_topology_store() -> None:
    ymmsl_text = (
            'version: v0.1\n'
            'simulation:\n'
            '  name: test_model\n'
            '  compute_elements:\n'
            '    macro: macro_implementation\n'
            '    micro: micro_implementation\n'
            '  conduits:\n'
            '    macro.out: micro.in\n'
            '    micro.out: macro.in\n')

    store = TopologyStore(ymmsl_text)
    assert store.conduits[0].sender == 'macro.out'
    assert store.conduits[0].receiver == 'micro.in'
    assert store.conduits[1].sender == 'micro.out'
    assert store.conduits[1].receiver == 'macro.in'
