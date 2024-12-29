from copy import copy

import pytest

from libmuscle.planner.resources import Core, CoreSet, OnNodeResources, Resources


@pytest.fixture
def c1():
    return Core(0, {0, 1})


def test_core_equals(c1):
    c2 = Core(0, {0, 1})
    c3 = Core(1, {0, 1})
    c4 = Core(0, {2, 3})

    assert c1 == c2
    assert not c1 != c2
    assert c1 != c3
    assert c1 != c4
    assert c3 != c4


def test_core_length(c1):
    assert len(c1) == 2

    c2 = Core(1, {4, 5, 6, 7})
    assert len(c2) == 4


def test_core_copy(c1):
    c2 = copy(c1)
    assert c2.cid == 0
    assert c2.hwthreads == {0, 1}

    c2.hwthreads.add(2)
    assert c1.hwthreads == {0, 1}
    assert c2.hwthreads == {0, 1, 2}


def test_core_union():
    c1 = Core(3, {3})
    c2 = Core(3, {4})

    assert c1 | c2 == Core(3, {3, 4})

    c3 = Core(2, {2})
    with pytest.raises(ValueError):
        c1 | c3


def test_core_union_onto(c1):
    c2 = Core(0, {2, 3})

    c1 |= c2
    assert c1.hwthreads == {0, 1, 2, 3}
    assert c2.hwthreads == {2, 3}

    c3 = Core(3, {6, 7})
    with pytest.raises(ValueError):
        c1 |= c3


def test_core_subtract():
    c1 = Core(0, {0, 1, 2, 3})
    c2 = Core(0, {0, 3})

    c1 -= c2
    assert c1.cid == 0
    assert c1.hwthreads == {1, 2}

    c3 = Core(0, {2, 3})
    c1 -= c3
    assert c1.cid == 0
    assert c1.hwthreads == {1}

    c4 = Core(1, {1, 2})
    with pytest.raises(ValueError):
        c1 -= c4


def test_core_isdisjoint(c1):
    c2 = Core(0, {0})
    c3 = Core(0, {2, 3})
    c4 = Core(1, {0, 1})

    assert not c1.isdisjoint(c2)
    assert not c2.isdisjoint(c1)
    assert c1.isdisjoint(c3)

    with pytest.raises(ValueError):
        c1.isdisjoint(c4)


def test_core_str(c1):
    assert str(c1) == '0(0,1)'


def test_core_repr(c1):
    assert repr(c1) == 'Core(0, {0,1})'


@pytest.fixture
def cs1():
    return CoreSet([Core(0, {0, 1}), Core(1, {2, 3})])


def test_core_set_equals(cs1):
    cs2 = CoreSet([Core(0, {0, 1}), Core(1, {2, 3})])
    cs3 = CoreSet([Core(1, {2, 3})])
    cs4 = CoreSet([])
    cs5 = CoreSet([Core(0, {0, 1}), Core(1, {2, 3}), Core(2, {4, 5})])
    cs6 = CoreSet([Core(3, {6, 7})])

    assert cs1 == cs2
    assert not cs1 != cs2
    assert cs1 != cs3
    assert cs1 != cs4
    assert cs1 != cs5
    assert cs1 != cs6
    assert not cs3 == cs4
    assert cs4 != cs5


def test_core_set_length(cs1):
    cs2 = CoreSet([])
    cs3 = CoreSet([Core(3, {6, 7})])

    assert len(cs1) == 2
    assert len(cs2) == 0
    assert len(cs3) == 1


def test_core_set_iter(cs1):
    for i, core in enumerate(cs1):
        assert i == core.cid
        assert core.hwthreads == {i * 2, i * 2 + 1}

    assert i == 1


def test_core_set_copy(cs1):
    cs2 = copy(cs1)
    assert cs1 == cs2

    cs2._cores[2] = Core(2, {4, 5})
    assert len(cs1._cores) == 2

    cs2._cores[0].hwthreads.add(2)
    assert 2 not in cs1._cores[0].hwthreads


def test_core_set_union_onto(cs1):
    cs2 = CoreSet([Core(3, {6, 7})])
    cs1 |= cs2

    assert len(cs1) == 3
    assert 0 in cs1._cores
    assert cs1._cores[0].cid == 0
    assert cs1._cores[0].hwthreads == {0, 1}
    assert 1 in cs1._cores
    assert cs1._cores[1].cid == 1
    assert cs1._cores[1].hwthreads == {2, 3}
    assert 3 in cs1._cores
    assert cs1._cores[3].cid == 3
    assert cs1._cores[3].hwthreads == {6, 7}

    assert id(cs1._cores[3]) != id(cs2._cores[3])
    assert id(cs1._cores[3].hwthreads) != id(cs2._cores[3].hwthreads)


def test_core_set_subtract_disjunct(cs1):
    cs2 = CoreSet([Core(3, {6, 7})])
    cs1 -= cs2

    assert len(cs1) == 2
    assert 0 in cs1._cores
    assert 1 in cs1._cores

    assert len(cs2) == 1
    assert 3 in cs2._cores


def test_core_set_subtract_whole_core(cs1):
    cs2 = CoreSet([Core(0, {0, 1})])
    cs1 -= cs2

    assert len(cs1) == 1
    assert 0 not in cs1._cores
    assert 1 in cs1._cores

    assert len(cs2) == 1
    assert 0 in cs2._cores


def test_core_set_subtract_threads(cs1):
    cs2 = CoreSet([Core(1, {2})])
    i1 = id(cs1._cores[1])

    cs1 -= cs2

    assert len(cs1) == 2
    assert 0 in cs1._cores
    assert 1 in cs1._cores
    assert id(cs1._cores[1]) == i1
    assert len(cs1._cores[1]) == 1
    assert cs1._cores[1].hwthreads == {3}
    assert cs1._cores[0].hwthreads == {0, 1}


def test_core_set_str(cs1):
    assert str(cs1) == '0-1(0-3)'


def test_core_set_repr(cs1):
    assert repr(cs1) == 'CoreSet({Core(0, {0,1}), Core(1, {2,3})})'


def test_core_set_get_first_cores(cs1):
    assert cs1.get_first_cores(0)._cores == {}
    assert cs1.get_first_cores(1)._cores == {0: Core(0, {0, 1})}
    assert cs1.get_first_cores(2)._cores == {
            0: Core(0, {0, 1}),
            1: Core(1, {2, 3})}
    with pytest.raises(RuntimeError):
        cs1.get_first_cores(3)


@pytest.fixture
def n1(cs1):
    return OnNodeResources('node001', cs1)


def test_node_resources_equals(n1):
    n2 = OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})]))
    n3 = OnNodeResources('node002', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})]))
    n4 = OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(1, {4, 3})]))

    assert n1 == n2
    assert n1 != n3
    assert n1 != n4


def test_node_resources_copy(n1):
    n2 = copy(n1)

    assert n1 == n2
    assert id(n1.cpu_cores) != id(n2.cpu_cores)
    assert id(n1.cpu_cores._cores[0]) != id(n2.cpu_cores._cores[0])
    assert id(n1.cpu_cores._cores[1].hwthreads) != id(n2.cpu_cores._cores[1].hwthreads)


def test_node_resources_union_onto(n1):
    n2 = OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(4, {8, 9, 10, 11})]))
    n3 = OnNodeResources('node001', CoreSet([Core(0, {3})]))
    n4 = OnNodeResources('node002', CoreSet([Core(3, {3})]))

    n1 |= n2

    assert len(n1.cpu_cores) == 3
    assert id(n1.cpu_cores._cores[4]) != id(n2.cpu_cores._cores[4])

    n1 |= n3

    assert len(n1.cpu_cores) == 3
    assert n1.cpu_cores._cores[0].hwthreads == {0, 1, 3}

    with pytest.raises(ValueError):
        n1 |= n4


def test_node_resources_hwthreads(n1):
    assert list(n1.hwthreads()) == [0, 1, 2, 3]


def test_node_resources_subtract(n1):
    n2 = OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(4, {8, 9, 10, 11})]))
    n3 = OnNodeResources('node001', CoreSet([Core(1, {3})]))
    n4 = OnNodeResources('node002', CoreSet([Core(3, {3})]))

    n1 -= n2

    assert len(n1.cpu_cores) == 1
    assert len(n1.cpu_cores._cores[1]) == 2

    n1 -= n3

    assert len(n1.cpu_cores) == 1
    assert len(n1.cpu_cores._cores[1]) == 1

    with pytest.raises(ValueError):
        n1 -= n4


@pytest.fixture
def r1(n1):
    return Resources([n1])


def test_resources_length(r1, n1):
    r2 = Resources([n1, OnNodeResources('node002', CoreSet([Core(0, {0, 1})]))])

    assert len(r1) == 1
    assert len(r2) == 2


def test_resources_iter(cs1, n1):
    n2 = OnNodeResources('node004', cs1)
    n3 = OnNodeResources('node002', CoreSet([Core(3, {3})]))
    nodes = [n1, n2, n3]
    res = Resources(nodes)

    for i, n in enumerate(res):
        assert n == nodes[i]


def test_resources_equals(r1):
    assert r1 == Resources(
            [OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})]))])

    r2 = Resources(
            [OnNodeResources('node002', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})]))])
    assert r1 != r2

    r3 = Resources(
            [OnNodeResources(
                'node001', CoreSet([Core(0, {0, 1}), Core(1, {1, 2, 3})]))])
    assert r1 != r3

    r4 = Resources([OnNodeResources('node001', CoreSet([Core(1, {1, 2})]))])
    assert r1 != r4

    r5 = Resources([
            OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})])),
            OnNodeResources('node002', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})]))
            ])
    assert r1 != r5


def test_resources_copy(r1):
    r2 = copy(r1)
    assert id(r2._nodes['node001']) != id(r1._nodes['node001'])
    assert id(r2._nodes['node001'].cpu_cores) != id(r1._nodes['node001'].cpu_cores)


def test_resources_union_onto(r1):
    r2 = Resources([])
    r2 |= r1
    assert r2 == r1

    r3 = Resources([OnNodeResources('node002', CoreSet([Core(0, {0})]))])
    r3 |= r1
    assert len(r3._nodes) == 2
    assert id(r3._nodes['node001']) != id(r1._nodes['node001'])
    assert sorted(r3._nodes.keys()) == ['node001', 'node002']


def test_resources_subtract(r1):
    r2 = Resources([])
    r2 -= r1
    assert len(r2._nodes) == 0

    r1 -= r2
    assert len(r1._nodes) == 1

    r3 = Resources([OnNodeResources('node001', CoreSet([Core(0, {0})]))])
    r1 -= r3
    assert len(r1._nodes) == 1
    assert r1._nodes['node001'].cpu_cores._cores[0].hwthreads == {1}


def test_resources_nodes():
    r1 = Resources([
        OnNodeResources('node001', CoreSet([Core(0, {0})])),
        OnNodeResources('node003', CoreSet([Core(1, {1})])),
        OnNodeResources('node004', CoreSet([Core(2, {2})]))])

    assert sorted(r1.nodes()) == ['node001', 'node003', 'node004']


def test_resources_total_cores():
    r1 = Resources([
        OnNodeResources('node001', CoreSet([Core(0, {0, 1})])),
        OnNodeResources('node003', CoreSet([Core(1, {1}), Core(5, {5})])),
        OnNodeResources('node004', CoreSet([Core(2, {2})]))])

    assert r1.total_cores() == 4


def test_resource_hwthreads(n1, r1):
    hwthreads = list(r1.hwthreads())
    assert hwthreads == [('node001', 0), ('node001', 1), ('node001', 2), ('node001', 3)]

    n2 = OnNodeResources('node007', CoreSet([Core(7, {7}), Core(3, {3})]))
    res = Resources([n1, n2])

    hwthreads = list(res.hwthreads())
    assert hwthreads == [
            ('node001', 0), ('node001', 1), ('node001', 2), ('node001', 3),
            ('node007', 7), ('node007', 3)]


def test_resources_isdisjoint(r1):
    r2 = Resources([])
    assert r1.isdisjoint(r2)

    r3 = Resources([OnNodeResources('node001', CoreSet([Core(0, {0})]))])
    assert not r1.isdisjoint(r3)

    r4 = Resources([OnNodeResources('node001', CoreSet([Core(0, {2})]))])
    assert r1.isdisjoint(r4)

    r5 = Resources([OnNodeResources('node002', CoreSet([Core(0, {0})]))])
    assert r1.isdisjoint(r5)


def test_resources_union(r1):
    r2 = Resources([])
    r3 = Resources([OnNodeResources('node001', CoreSet([Core(0, {0})]))])
    r4 = Resources([OnNodeResources('node001', CoreSet([Core(0, {2})]))])
    r5 = Resources([OnNodeResources('node002', CoreSet([Core(0, {0})]))])

    assert Resources.union([r1, r2]) == r1
    assert Resources.union([r1, r3]) == r1
    assert Resources.union([r1, r4]) == Resources([
        OnNodeResources('node001', CoreSet([Core(0, {0, 1, 2}), Core(1, {2, 3})]))])

    assert Resources.union([r1, r5]) == Resources([
        OnNodeResources('node001', CoreSet([Core(0, {0, 1}), Core(1, {2, 3})])),
        OnNodeResources('node002', CoreSet([Core(0, {0})]))])

    assert Resources.union([r1, r2, r3, r4, r5]) == Resources([
        OnNodeResources('node001', CoreSet([Core(0, {0, 1, 2}), Core(1, {2, 3})])),
        OnNodeResources('node002', CoreSet([Core(0, {0})]))])
