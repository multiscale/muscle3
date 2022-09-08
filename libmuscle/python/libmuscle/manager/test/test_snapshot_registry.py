from unittest.mock import MagicMock

import pytest
from libmuscle.snapshot import SnapshotMetadata
from ymmsl import (
        Configuration, Model, Component, Conduit, Implementation,
        ImplementationState as IState, Reference)

from libmuscle.manager.snapshot_registry import (
    SnapshotRegistry, calc_consistency, calc_consistency_list, safe_get,
    _ConnectionInfo)


def make_snapshot(**msg_counts) -> SnapshotMetadata:
    return SnapshotMetadata([], 0, 0, 0, {**msg_counts}, False, '')


@pytest.fixture(params=[True, False])
def micro_is_stateless(request: pytest.FixtureRequest) -> bool:
    return request.param


@pytest.fixture
def macro_micro(micro_is_stateless: bool) -> Configuration:
    components = [
            Component('macro', 'macro_impl'),
            Component('micro', 'micro_impl')]
    conduits = [
            Conduit('macro.o_i', 'micro.f_i'),
            Conduit('micro.o_f', 'macro.s')]
    model = Model('macro_micro', components, conduits)

    if micro_is_stateless:
        micro_impl = Implementation(
                'micro_impl', stateful=IState.STATELESS, executable='pass')
    else:
        micro_impl = Implementation(
                'micro_impl', supports_checkpoint=True, executable='pass')

    implementations = [
            Implementation(
                    'macro_impl', supports_checkpoint=True, executable='pass'),
            micro_impl]

    return Configuration(model, implementations=implementations)


@pytest.fixture
def uq(macro_micro: Configuration) -> Configuration:
    for component in macro_micro.model.components:
        component.multiplicity = [5]
    macro_micro.model.components.append(Component('qmc', 'qmc_impl'))
    macro_micro.model.components.append(Component('rr', 'rr_impl'))
    macro_micro.model.conduits.extend([
            Conduit('qmc.parameters_out', 'rr.front_in'),
            Conduit('rr.front_out', 'qmc.states_in'),
            Conduit('rr.back_out', 'macro.muscle_settings_in'),
            Conduit('macro.final_state_out', 'rr.back_in')])
    macro_micro.implementations[Reference('qmc_impl')] = Implementation(
            'qmc_impl', supports_checkpoint=True, executable='pass')
    macro_micro.implementations[Reference('rr_impl')] = Implementation(
            'rr_impl', supports_checkpoint=True, executable='pass')
    return macro_micro


def test_safe_get() -> None:
    assert safe_get([], 0, 1) == 1
    assert safe_get([3], 0, 1) == 3
    assert safe_get([3], 1, 5) == 5
    for i in range(10):
        expected = -1 if i >= 3 else i + 3
        assert safe_get([3, 4, 5], i, -1) == expected


def test_calc_consistency() -> None:
    num_sent = 3
    for num_received in [2, 3, 4, 5]:
        consistent = num_received in [3, 4]
        assert calc_consistency(num_sent, num_received, True) is consistent
        assert calc_consistency(num_received, num_sent, False) is consistent

    num_received = 10
    for num_sent in [8, 9, 10, 11]:
        consistent = num_sent in [9, 10]
        assert calc_consistency(num_sent, num_received, True) is consistent
        assert calc_consistency(num_received, num_sent, False) is consistent


def test_calc_consistency_list() -> None:
    num_sent = [3, 3]
    for num_received in [[2, 3], [3, 2], [3, 5], [], [4, 4, 0, 0, 2]]:
        assert not calc_consistency_list(num_sent, num_received, True)
        assert not calc_consistency_list(num_received, num_sent, False)
    for num_received in [[3, 3], [3, 4], [4, 3], [4, 4],
                         [3, 3, 1], [4, 4, 0, 0, 0, 1, 0, 1]]:
        assert calc_consistency_list(num_sent, num_received, True)
        assert calc_consistency_list(num_received, num_sent, False)


def test_stateful_peers(uq: Configuration, micro_is_stateless: bool) -> None:
    snapshot_registry = SnapshotRegistry(uq)
    macro = Reference('macro')
    micro = Reference('micro')
    qmc = Reference('qmc')
    rr = Reference('rr')

    expected_stateful = {qmc, rr} | {macro + i for i in range(5)}
    if not micro_is_stateless:
        expected_stateful.update(micro + i for i in range(5))
    assert snapshot_registry._stateful_instances == expected_stateful

    assert snapshot_registry._get_stateful_peers(qmc) == {rr}
    expected_rr_peers = {qmc} | {macro + i for i in range(5)}
    assert snapshot_registry._get_stateful_peers(rr) == expected_rr_peers
    for i in range(5):
        expected_peers = {rr} if micro_is_stateless else {rr, micro + i}
        assert snapshot_registry._get_stateful_peers(macro + i) == expected_peers
        assert snapshot_registry._get_stateful_peers(micro + i) == {macro + i}


def test_connections(uq: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(uq)
    macro = Reference('macro')
    micro = Reference('micro')
    qmc = Reference('qmc')
    rr = Reference('rr')

    assert not snapshot_registry._get_connections(qmc, macro + 1)
    assert not snapshot_registry._get_connections(macro + 3, qmc)
    assert not snapshot_registry._get_connections(qmc, micro + 0)
    assert not snapshot_registry._get_connections(micro + 1, qmc)
    assert not snapshot_registry._get_connections(rr, micro + 4)
    assert not snapshot_registry._get_connections(micro + 0, rr)

    connections = snapshot_registry._get_connections(rr, qmc)
    assert len(connections) == 2
    for rr_port, qmc_port, info in connections:
        assert rr_port in (Reference('front_out'), Reference('front_in'))
        assert qmc_port in (Reference('parameters_out'), Reference('states_in'))
        is_sending = bool(info & _ConnectionInfo.SELF_IS_SENDING)
        assert is_sending is (rr_port == Reference('front_out'))
        # Note: actually both are vector ports, but this is undetectable from
        # the ymmsl configuration. Luckily we treat it the same as scalar-scalar
        assert not (info & _ConnectionInfo.SELF_IS_VECTOR)
        assert not (info & _ConnectionInfo.PEER_IS_VECTOR)

    connections = snapshot_registry._get_connections(macro + 0, rr)
    assert len(connections) == 2
    for macro_port, rr_port, info in connections:
        assert macro_port in (
                Reference('muscle_settings_in'), Reference('final_state_out'))
        assert rr_port in (Reference('back_out'), Reference('back_in'))
        is_sending = bool(info & _ConnectionInfo.SELF_IS_SENDING)
        assert is_sending is (macro_port == Reference('final_state_out'))
        assert not (info & _ConnectionInfo.SELF_IS_VECTOR)
        assert (info & _ConnectionInfo.PEER_IS_VECTOR)

    connections = snapshot_registry._get_connections(rr, macro + 1)
    assert len(connections) == 2
    for rr_port, macro_port, info in connections:
        assert macro_port in (
                Reference('muscle_settings_in'), Reference('final_state_out'))
        assert rr_port in (Reference('back_out'), Reference('back_in'))
        is_sending = bool(info & _ConnectionInfo.SELF_IS_SENDING)
        assert is_sending is (rr_port == Reference('back_out'))
        assert (info & _ConnectionInfo.SELF_IS_VECTOR)
        assert not (info & _ConnectionInfo.PEER_IS_VECTOR)


def test_macro_micro_snapshots(
        macro_micro: Configuration, micro_is_stateless: bool) -> None:
    snapshot_registry = SnapshotRegistry(macro_micro)
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()
    macro = Reference('macro')
    micro = Reference('micro')

    macro_snapshot = make_snapshot(o_i=[3], s=[3])
    snapshot_registry.register_snapshot(macro, macro_snapshot)

    assert len(snapshot_registry._snapshots[macro]) == 1
    node = snapshot_registry._snapshots[macro][0]
    assert node.consistent is micro_is_stateless
    assert node.consistent_peers == {}
    assert node.instance == macro
    assert node.num == 1
    assert node.snapshot is macro_snapshot
    if micro_is_stateless:
        assert node.stateful_peers == set()
        snapshot_registry._write_snapshot_ymmsl.assert_called_once_with([node])
        snapshot_registry._write_snapshot_ymmsl.reset_mock()
    else:
        assert node.stateful_peers == {micro}
        snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    if not micro_is_stateless:
        # Note: this snapshot is not realistic, it should have come in before
        # the macro snapshot above. However, it's still useful for testing the
        # consistency algorithm
        micro_snapshot = make_snapshot(f_i=[2], o_f=[1])
        snapshot_registry.register_snapshot(micro, micro_snapshot)

        assert len(snapshot_registry._snapshots[micro]) == 1
        assert not snapshot_registry._snapshots[micro][0].consistent
        snapshot_registry._write_snapshot_ymmsl.assert_not_called()

        micro_snapshot = make_snapshot(f_i=[3], o_f=[2])
        snapshot_registry.register_snapshot(micro, micro_snapshot)

        # micro snapshots should be cleaned up now!
        assert len(snapshot_registry._snapshots[micro]) == 1
        micro_node = snapshot_registry._snapshots[micro][0]
        assert micro_node.consistent
        snapshot_registry._write_snapshot_ymmsl.assert_called_with(
                [micro_node, node])
        snapshot_registry._write_snapshot_ymmsl.reset_mock()

        micro_snapshot = make_snapshot(f_i=[4], o_f=[3])
        snapshot_registry.register_snapshot(micro, micro_snapshot)

        # micro snapshots should be cleaned up now!
        assert len(snapshot_registry._snapshots[micro]) == 1
        micro_node = snapshot_registry._snapshots[micro][0]
        assert micro_node.consistent
        snapshot_registry._write_snapshot_ymmsl.assert_called_with(
                [micro_node, node])
        snapshot_registry._write_snapshot_ymmsl.reset_mock()

    macro_snapshot = make_snapshot(o_i=[4], s=[4])
    snapshot_registry.register_snapshot(macro, macro_snapshot)
    snapshot_registry._write_snapshot_ymmsl.assert_called_once()


def test_uq(uq: Configuration, micro_is_stateless: bool) -> None:
    snapshot_registry = SnapshotRegistry(uq)
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()
    macro = Reference('macro')
    micro = Reference('micro')
    qmc = Reference('qmc')
    rr = Reference('rr')

    qmc_snapshot = make_snapshot(parameters_out=[], states_in=[])
    snapshot_registry.register_snapshot(qmc, qmc_snapshot)

    rr_snapshot = make_snapshot(
            front_in=[1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
            front_out=[0] * 10,
            back_out=[1, 1, 1, 1, 1],
            back_in=[0] * 5)
    snapshot_registry.register_snapshot(rr, rr_snapshot)
    node = snapshot_registry._snapshots[rr][-1]
    assert qmc in node.consistent_peers
    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    macro_snapshot = make_snapshot(
            muscle_settings_in=[1], final_state_out=[0], o_i=[0], s=[0])
    for i in range(5):
        snapshot_registry.register_snapshot(macro + i, macro_snapshot)
        node = snapshot_registry._snapshots[macro + i][-1]
        assert node.consistent_peers.keys() == {rr}
        if micro_is_stateless and i == 4:
            snapshot_registry._write_snapshot_ymmsl.assert_called_once()
            snapshot_registry._write_snapshot_ymmsl.reset_mock()
        else:
            snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    if not micro_is_stateless:
        micro_snapshot = make_snapshot(f_i=[1], o_f=[0])
        for i in range(5):
            snapshot_registry.register_snapshot(micro + i, micro_snapshot)
            node = snapshot_registry._snapshots[micro + i][-1]
            assert node.consistent_peers.keys() == {macro + i}
            if i == 4:
                snapshot_registry._write_snapshot_ymmsl.assert_called_once()
                snapshot_registry._write_snapshot_ymmsl.reset_mock()
            else:
                snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    qmc_snapshot = make_snapshot(parameters_out=[1, 1, 1, 1, 1], states_in=[])
    snapshot_registry.register_snapshot(qmc, qmc_snapshot)
    node = snapshot_registry._snapshots[qmc][-1]
    assert node.consistent_peers.keys() == {rr}
    snapshot_registry._write_snapshot_ymmsl.assert_called_once()
    snapshot_registry._write_snapshot_ymmsl.reset_mock()
    assert len(snapshot_registry._snapshots[qmc]) == 1  # previous is cleaned up


def test_heuristic_rollbacks() -> None:
    components = [Component(f'comp{i}', f'impl{i}') for i in range(4)]
    conduits = [Conduit(f'comp{i}.o_f', f'comp{i+1}.f_i') for i in range(3)]
    model = Model('linear', components, conduits)
    implementations = [
            Implementation(f'impl{i}', supports_checkpoint=True, script='xyz')
            for i in range(4)]
    config = Configuration(model, implementations=implementations)

    comp1, comp2, comp3, comp4 = (Reference(f'comp{i}') for i in range(4))

    snapshot_registry = SnapshotRegistry(config)
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()

    for i in range(4):
        snapshot_registry.register_snapshot(comp1, make_snapshot(o_f=[i]))
    assert len(snapshot_registry._snapshots[comp1]) == 4

    for i in range(10):
        snapshot_registry.register_snapshot(
                comp2, make_snapshot(f_i=[1], o_f=[0]))
        snapshot_registry.register_snapshot(
                comp3, make_snapshot(f_i=[1], o_f=[0]))
    assert len(snapshot_registry._snapshots[comp2]) == 10
    assert len(snapshot_registry._snapshots[comp3]) == 10

    snapshot_registry.register_snapshot(comp2, make_snapshot(f_i=[2], o_f=[1]))
    assert len(snapshot_registry._snapshots[comp2]) == 11
    snapshot_registry.register_snapshot(comp2, make_snapshot(f_i=[3], o_f=[2]))
    assert len(snapshot_registry._snapshots[comp2]) == 12

    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    snapshot_registry.register_snapshot(
            comp4, make_snapshot(f_i=[1]))
    snapshot_registry._write_snapshot_ymmsl.assert_called()

    assert len(snapshot_registry._snapshots[comp1]) == 2
    assert len(snapshot_registry._snapshots[comp2]) == 2
    assert len(snapshot_registry._snapshots[comp3]) == 1
    assert len(snapshot_registry._snapshots[comp4]) == 1
