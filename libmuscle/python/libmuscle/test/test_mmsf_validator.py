from logging import WARNING
from typing import Any
from unittest.mock import Mock

import pytest
from ymmsl import Operator, Reference

from libmuscle.port_manager import PortManager
from libmuscle.mmsf_validator import MMSFValidator


class Contains:
    """Helper class to simplify tests using caplog.record_tuples"""
    def __init__(self, value: Any) -> None:
        self.value = value

    def __eq__(self, other: Any) -> bool:
        return self.value in other

    def __repr__(self) -> str:
        return f"Contains({self.value!r})"


@pytest.fixture
def mock_peer_info() -> Mock:
    # Create a mock PeerInfo indicating that all ports are connected
    peer_info = Mock()
    peer_info.is_connected.return_value = True
    peer_info.get_peer_ports.return_value = [Reference("test")]
    peer_info.get_peer_dims.return_value = []
    return peer_info


@pytest.fixture
def validator_simple(mock_peer_info) -> MMSFValidator:
    port_manager = PortManager([], {
            Operator.F_INIT: ["f_i"],
            Operator.O_I: ["o_i"],
            Operator.S: ["s"],
            Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    return MMSFValidator(port_manager)


@pytest.mark.parametrize("num_iterations", [0, 1, 2])
@pytest.mark.parametrize("num_reuse", [1, 5])
def test_simple_correct(num_iterations, num_reuse, validator_simple, caplog):
    for _ in range(num_reuse):
        validator_simple.reuse_instance()
        validator_simple.check_receive("f_i", None)
        for _ in range(num_iterations):
            validator_simple.check_send("o_i", None)
            validator_simple.check_receive("s", None)
        validator_simple.check_send("o_f", None)
    # Final reuse_instance()
    validator_simple.reuse_instance()
    assert caplog.record_tuples == []


def test_simple_skip_f_init(validator_simple, caplog):
    validator_simple.reuse_instance()
    validator_simple.check_send("o_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Send on port 'o_i'"))]


def test_simple_skip_o_i(validator_simple, caplog):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)

    validator_simple.check_receive("f_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Receive on port 'f_i'"))]

    caplog.clear()
    validator_simple.check_receive("s", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Receive on port 's'"))]

    caplog.clear()
    validator_simple.reuse_instance()
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("reuse_instance()"))]


def test_simple_skip_s(validator_simple, caplog):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_send("o_i", None)

    validator_simple.check_send("o_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Send on port 'o_i'"))]

    caplog.clear()
    validator_simple.check_send("o_f", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Send on port 'o_f'"))]


def test_simple_skip_o_f(validator_simple, caplog):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_send("o_i", None)
    validator_simple.check_receive("s", None)

    validator_simple.reuse_instance()
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("reuse_instance()"))]


def test_simple_skip_reuse_instance(validator_simple, caplog):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_receive("o_f", None)

    validator_simple.check_receive("f_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Receive on port 'f_i'"))]


def test_only_o_f(mock_peer_info, caplog):
    port_manager = PortManager([], {Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_send("o_f", None)

    validator.check_send("o_f", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Send on port 'o_f'"))]


def test_only_f_i(mock_peer_info, caplog):
    port_manager = PortManager([], {Operator.F_INIT: ["f_i"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_receive("f_i", None)

    validator.check_receive("f_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Receive on port 'f_i'"))]


def test_micro(mock_peer_info, caplog):
    port_manager = PortManager([], {Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_receive("f_i", None)
        validator.check_send("o_f", None)
    validator.reuse_instance()
    validator.check_receive("f_i", None)

    validator.check_receive("f_i", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Receive on port 'f_i'"))]

    caplog.clear()
    validator.reuse_instance()
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("reuse_instance()"))]


def test_not_all_ports_used(mock_peer_info, caplog):
    port_manager = PortManager([], {
            Operator.F_INIT: ["f_i1", "f_i2"], Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    validator.reuse_instance()
    validator.check_receive("f_i1", None)

    validator.check_send("o_f", None)
    assert caplog.record_tuples == [
        ("libmuscle.mmsf_validator", WARNING, Contains("Send on port 'o_f'"))]
