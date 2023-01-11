from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from ymmsl import (
        Configuration, Model, Component, Conduit, Implementation,
        KeepsStateForNextUse, Reference)

from libmuscle.manager.snapshot_registry import (
    SnapshotNode, SnapshotRegistry, calc_consistency, calc_consistency_list,
    safe_get, _ConnectionInfo)
from libmuscle.manager.topology_store import TopologyStore
from libmuscle.snapshot import SnapshotMetadata


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
                'micro_impl',
                keeps_state_for_next_use=KeepsStateForNextUse.NO,
                executable='pass')
    else:
        micro_impl = Implementation('micro_impl', executable='pass')

    implementations = [
            Implementation('macro_impl', executable='pass'),
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
            'qmc_impl', executable='pass')
    macro_micro.implementations[Reference('rr_impl')] = Implementation(
            'rr_impl', executable='pass')
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
        expect = num_received in [3, 4]
        assert calc_consistency(num_sent, num_received, True, False) is expect
        assert calc_consistency(num_received, num_sent, False, False) is expect

    num_received = 10
    for num_sent in [8, 9, 10, 11]:
        expect = num_sent in [9, 10]
        assert calc_consistency(num_sent, num_received, True, False) is expect
        assert calc_consistency(num_received, num_sent, False, False) is expect


def test_calc_consistency_with_restart() -> None:
    # Check normal rules
    assert calc_consistency(0, 0, True, True)
    assert calc_consistency(0, 0, False, True)
    assert not calc_consistency(1, 0, True, True)
    assert not calc_consistency(1, 0, True, False)
    assert calc_consistency(1, 0, False, False)
    # Different: num2 == 0 comes from the restarted actor, we do not want a
    # resume file to be created in this instance (because an instance further in
    # the call chain is ahead of the one that would be restarted):
    assert not calc_consistency(1, 0, False, True)


def test_calc_consistency_list() -> None:
    num_sent = [3, 3]
    for num_received in [[2, 3], [3, 2], [3, 5], [], [4, 4, 0, 0, 2]]:
        assert not calc_consistency_list(num_sent, num_received, True, False)
        assert not calc_consistency_list(num_received, num_sent, False, False)
    for num_received in [[3, 3], [3, 4], [4, 3], [4, 4],
                         [3, 3, 1], [4, 4, 0, 0, 0, 1, 0, 1]]:
        assert calc_consistency_list(num_sent, num_received, True, False)
        assert calc_consistency_list(num_received, num_sent, False, False)


def test_write_ymmsl(tmp_path: Path):
    configuration = Configuration(Model('empty', []))
    snapshot_registry = SnapshotRegistry(
            configuration, tmp_path, TopologyStore(configuration))
    snapshot_registry._write_snapshot_ymmsl([])

    paths = list(tmp_path.iterdir())
    assert len(paths) == 1
    assert paths[0].suffix == ".ymmsl"
    paths[0].unlink()

    now = datetime.now()
    for seconds in range(3):
        time = (now + timedelta(seconds=seconds)).strftime("%Y%m%d_%H%M%S")
        (tmp_path / f'snapshot_{time}.ymmsl').touch()
    snapshot_registry._write_snapshot_ymmsl([])
    paths = list(tmp_path.iterdir())
    assert len(paths) == 4
    paths = list(tmp_path.glob('*_1.ymmsl'))
    assert len(paths) == 1


def test_snapshot_config():
    configuration = Configuration(Model('empty', []))
    snapshot_registry = SnapshotRegistry(
            configuration, None, TopologyStore(configuration))
    micro_metadata = SnapshotMetadata(
            ['simulation_time >= 24.0', 'wallclocktime >= 10'],
            10.123456789, 24.3456789, None, {}, False, 'micro_snapshot')
    macro_metadata = SnapshotMetadata(
            ['simulation_time >= 12.0', 'wallclocktime >= 10'],
            10.123456789, 12.3456789, None, {}, False, 'macro_snapshot')
    snapshots = [
            SnapshotNode(1, Reference('micro'), micro_metadata, set()),
            SnapshotNode(1, Reference('macro'), macro_metadata, set())]

    now = datetime.now()
    config = snapshot_registry._generate_snapshot_config(snapshots, now)
    assert len(config.resume) == 2
    assert config.resume[Reference('macro')] == Path('macro_snapshot')
    assert config.resume[Reference('micro')] == Path('micro_snapshot')
    # note: no automatic testing for formatting, should verify by eye if this
    # looks okay..
    print(config.description)

    long_metadata = SnapshotMetadata(
            ['simulation_time >= 24.0'], 1.23456789e-10, 1.23456789e10, None,
            {}, False, '/this/is/a/long/path/to/the/snapshot/file.pack')
    snapshots.append(SnapshotNode(
            1, Reference('this.is.a.long.reference[10]'), long_metadata, set()))

    config = snapshot_registry._generate_snapshot_config(snapshots, now)
    assert len(config.resume) == 3
    assert config.resume[Reference('this.is.a.long.reference[10]')] == Path(
            '/this/is/a/long/path/to/the/snapshot/file.pack')
    print(config.description)


def test_peers(uq: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(uq, None, TopologyStore(uq))
    macro = Reference('macro')
    micro = Reference('micro')
    qmc = Reference('qmc')
    rr = Reference('rr')

    all_instances = {qmc, rr} | {macro + i for i in range(5)}
    all_instances.update(micro + i for i in range(5))
    assert snapshot_registry._instances == all_instances

    assert snapshot_registry._get_peers(qmc) == {rr}
    expected_rr_peers = {qmc} | {macro + i for i in range(5)}
    assert snapshot_registry._get_peers(rr) == expected_rr_peers
    for i in range(5):
        assert snapshot_registry._get_peers(macro + i) == {rr, micro + i}
        assert snapshot_registry._get_peers(micro + i) == {macro + i}


def test_connections(uq: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(uq, None, TopologyStore(uq))
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


def test_implementation(uq: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(uq, None, TopologyStore(uq))

    qmc_impl = snapshot_registry._implementation(Reference('qmc'))
    assert qmc_impl.name == 'qmc_impl'

    missing_impl = snapshot_registry._implementation(Reference('missing'))
    assert missing_impl is None


def test_macro_micro_snapshots(macro_micro: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(
            macro_micro, None, TopologyStore(macro_micro))
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()
    macro = Reference('macro')
    micro = Reference('micro')

    macro_snapshot = make_snapshot(o_i=[3], s=[3])
    snapshot_registry._add_snapshot(macro, macro_snapshot)

    assert len(snapshot_registry._snapshots[macro]) == 1
    node = snapshot_registry._snapshots[macro][0]
    assert node.consistent is False
    assert node.consistent_peers == {}
    assert node.instance == macro
    assert node.num == 1
    assert node.snapshot is macro_snapshot
    assert node.peers == {micro}
    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    # Note: this snapshot is not realistic, it should have come in before
    # the macro snapshot above. However, it's still useful for testing the
    # consistency algorithm
    micro_snapshot = make_snapshot(f_i=[2], o_f=[1])
    snapshot_registry._add_snapshot(micro, micro_snapshot)

    assert len(snapshot_registry._snapshots[micro]) == 1
    assert snapshot_registry._snapshots[micro][0].consistent is False
    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    micro_snapshot = make_snapshot(f_i=[3], o_f=[2])
    snapshot_registry._add_snapshot(micro, micro_snapshot)

    # The first micro snapshots should be cleaned up now
    assert len(snapshot_registry._snapshots[micro]) == 1
    micro_node = snapshot_registry._snapshots[micro][0]
    assert micro_node.consistent
    snapshot_registry._write_snapshot_ymmsl.assert_called_once_with(
            [micro_node, node])
    snapshot_registry._write_snapshot_ymmsl.reset_mock()

    # 3 micro snapshots in the same reuse:
    for _ in range(3):
        micro_snapshot = make_snapshot(f_i=[4], o_f=[3])
        snapshot_registry._add_snapshot(micro, micro_snapshot)

    # Previous micro snapshot should be cleaned up now
    assert len(snapshot_registry._snapshots[micro]) == 1
    micro_node = snapshot_registry._snapshots[micro][-1]
    assert snapshot_registry._write_snapshot_ymmsl.call_count == 3
    snapshot_registry._write_snapshot_ymmsl.assert_called_with(
            [micro_node, node])
    snapshot_registry._write_snapshot_ymmsl.reset_mock()

    macro_snapshot = make_snapshot(o_i=[4], s=[4])
    snapshot_registry._add_snapshot(macro, macro_snapshot)
    snapshot_registry._write_snapshot_ymmsl.assert_called_once()
    snapshot_registry._write_snapshot_ymmsl.reset_mock()

    # 3 micro snapshots in the same reuse, but inconcistent with previous macro
    for _ in range(3):
        micro_snapshot = make_snapshot(f_i=[6], o_f=[5])
        snapshot_registry._add_snapshot(micro, micro_snapshot)

    # All three should be present now in addition to the one last used in
    # workflow snapshot
    assert len(snapshot_registry._snapshots[micro]) == 4
    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    macro_snapshot = make_snapshot(o_i=[6], s=[6])
    snapshot_registry._add_snapshot(macro, macro_snapshot)
    assert snapshot_registry._write_snapshot_ymmsl.call_count == 3
    assert len(snapshot_registry._snapshots[micro]) == 1
    assert len(snapshot_registry._snapshots[macro]) == 1


def test_uq(uq: Configuration) -> None:
    snapshot_registry = SnapshotRegistry(uq, None, TopologyStore(uq))
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()
    macro = Reference('macro')
    micro = Reference('micro')
    qmc = Reference('qmc')
    rr = Reference('rr')

    qmc_snapshot = make_snapshot(parameters_out=[], states_in=[])
    snapshot_registry._add_snapshot(qmc, qmc_snapshot)

    rr_snapshot = make_snapshot(
            front_in=[1, 1, 1, 1, 1, 0, 0, 0, 0, 0],
            front_out=[0] * 10,
            back_out=[1, 1, 1, 1, 1],
            back_in=[0] * 5)
    snapshot_registry._add_snapshot(rr, rr_snapshot)
    node = snapshot_registry._snapshots[rr][-1]
    assert qmc in node.consistent_peers
    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    macro_snapshot = make_snapshot(
            muscle_settings_in=[1], final_state_out=[0], o_i=[0], s=[0])
    for i in range(5):
        snapshot_registry._add_snapshot(macro + i, macro_snapshot)
        node = snapshot_registry._snapshots[macro + i][-1]
        assert node.consistent_peers.keys() == {rr}
        snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    micro_snapshot = make_snapshot(f_i=[1], o_f=[0])
    for i in range(5):
        snapshot_registry._add_snapshot(micro + i, micro_snapshot)
        node = snapshot_registry._snapshots[micro + i][-1]
        assert node.consistent_peers.keys() == {macro + i}
        if i == 4:
            snapshot_registry._write_snapshot_ymmsl.assert_called_once()
            snapshot_registry._write_snapshot_ymmsl.reset_mock()
        else:
            snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    qmc_snapshot = make_snapshot(parameters_out=[1, 1, 1, 1, 1], states_in=[])
    snapshot_registry._add_snapshot(qmc, qmc_snapshot)
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
            Implementation(f'impl{i}', script='xyz')
            for i in range(4)]
    config = Configuration(model, implementations=implementations)

    comp1, comp2, comp3, comp4 = (Reference(f'comp{i}') for i in range(4))

    snapshot_registry = SnapshotRegistry(config, None, TopologyStore(config))
    # prevent actually writing a ymmsl file, testing that separately
    snapshot_registry._write_snapshot_ymmsl = MagicMock()

    for i in range(4):
        snapshot_registry._add_snapshot(comp1, make_snapshot(o_f=[i]))
    assert len(snapshot_registry._snapshots[comp1]) == 4

    for i in range(10):
        snapshot_registry._add_snapshot(
                comp2, make_snapshot(f_i=[1], o_f=[0]))
        snapshot_registry._add_snapshot(
                comp3, make_snapshot(f_i=[1], o_f=[0]))
    assert len(snapshot_registry._snapshots[comp2]) == 10
    assert len(snapshot_registry._snapshots[comp3]) == 10

    snapshot_registry._add_snapshot(comp2, make_snapshot(f_i=[2], o_f=[1]))
    assert len(snapshot_registry._snapshots[comp2]) == 11
    snapshot_registry._add_snapshot(comp2, make_snapshot(f_i=[3], o_f=[2]))
    assert len(snapshot_registry._snapshots[comp2]) == 12

    snapshot_registry._write_snapshot_ymmsl.assert_not_called()

    snapshot_registry._add_snapshot(
            comp4, make_snapshot(f_i=[1]))
    snapshot_registry._write_snapshot_ymmsl.assert_called()

    assert len(snapshot_registry._snapshots[comp1]) == 2
    assert len(snapshot_registry._snapshots[comp2]) == 2
    assert len(snapshot_registry._snapshots[comp3]) == 1
    assert len(snapshot_registry._snapshots[comp4]) == 1
