import pytest
from ymmsl import Identifier

from libmuscle.port import Operator, Port


def test_create_port():
    port = Port('out', Operator.O_I, False, True, 0, [])
    assert port.name == Identifier('out')
    assert port.operator == Operator.O_I
    assert port._length is None
    assert port._is_resizable is False
    assert port._is_connected is True


def test_create_invalid_port():
    with pytest.raises(RuntimeError):
        Port('out', Operator.O_I, True, True, 1, [])

    with pytest.raises(RuntimeError):
        Port('out', Operator.O_F, True, True, 0, [10, 10])

    with pytest.raises(RuntimeError):
        Port('out', Operator.O_F, False, True, 1, [11, 12])

    with pytest.raises(RuntimeError):
        Port('out', Operator.O_I, False, True, 2, [])


def test_port_properties():
    port = Port('out', Operator.O_F, False, False, 0, [])
    assert port.is_vector() is False
    assert port.is_resizable() is False
    assert port.is_connected() is False
    with pytest.raises(RuntimeError):
        port.get_length()
    with pytest.raises(RuntimeError):
        port.set_length(3)

    port = Port('out', Operator.O_F, True, True, 0, [10])
    assert port.is_vector() is True
    assert port.is_resizable() is False
    assert port.get_length() == 10
    with pytest.raises(RuntimeError):
        port.set_length(3)

    port = Port('out', Operator.O_F, False, True, 1, [10])
    assert port.is_vector() is False
    assert port.is_resizable() is False
    with pytest.raises(RuntimeError):
        port.get_length()
    with pytest.raises(RuntimeError):
        port.set_length(4)

    port = Port('out', Operator.O_F, True, True, 1, [10, 20])
    assert port.is_vector() is True
    assert port.is_resizable() is False
    assert port.get_length() == 20
    with pytest.raises(RuntimeError):
        port.set_length(5)

    port = Port('out', Operator.O_F, False, True, 2, [12])
    assert port.is_vector() is False
    assert port.is_resizable() is False
    with pytest.raises(RuntimeError):
        port.get_length()
    with pytest.raises(RuntimeError):
        port.set_length(9)

    port = Port('out', Operator.O_F, True, True, 1, [13])
    assert port.is_vector() is True
    assert port.is_resizable() is True
    assert port.get_length() == 0
    port.set_length(27)
    assert port.get_length() == 27
