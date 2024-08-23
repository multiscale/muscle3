from typing import Any
from unittest.mock import Mock

import pytest
from ymmsl import Operator, Reference

from libmuscle.port_manager import PortManager
from libmuscle.mmsf_validator import MMSFValidator


# For testing purposes we monkeypatch _logger.warning so it raises the following
# exception: ot is easier to verify that an exception is raised than checking that a
# warning message is logged.
class TestMMSFValidatorException(Exception):
    pass


@pytest.fixture(autouse=True)
def patch_logger_to_raise_error(monkeypatch):
    def raise_on_log(msg: str, *args: Any) -> None:
        raise TestMMSFValidatorException(msg % args)
    monkeypatch.setattr("libmuscle.mmsf_validator._logger.warning", raise_on_log)


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
def test_simple_correct(num_iterations, num_reuse, validator_simple):
    for _ in range(num_reuse):
        validator_simple.reuse_instance()
        validator_simple.check_receive("f_i", None)
        for _ in range(num_iterations):
            validator_simple.check_send("o_i", None)
            validator_simple.check_receive("s", None)
        validator_simple.check_send("o_f", None)
    # Final reuse_instance()
    validator_simple.reuse_instance()


def test_simple_skip_f_init(validator_simple):
    validator_simple.reuse_instance()
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_send("o_i", None)


def test_simple_skip_o_i(validator_simple):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_receive("f_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_receive("s", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.reuse_instance()


def test_simple_skip_s(validator_simple):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_send("o_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_send("o_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_send("o_f", None)


def test_simple_skip_o_f(validator_simple):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_send("o_i", None)
    validator_simple.check_receive("s", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.reuse_instance()


def test_simple_skip_reuse_instance(validator_simple):
    validator_simple.reuse_instance()
    validator_simple.check_receive("f_i", None)
    validator_simple.check_receive("o_f", None)
    with pytest.raises(TestMMSFValidatorException):
        validator_simple.check_receive("f_i", None)


def test_only_o_f(mock_peer_info):
    port_manager = PortManager([], {Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_send("o_f", None)
    with pytest.raises(TestMMSFValidatorException):
        validator.check_send("o_f", None)


def test_only_f_i(mock_peer_info):
    port_manager = PortManager([], {Operator.F_INIT: ["f_i"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_receive("f_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator.check_receive("f_i", None)


def test_micro(mock_peer_info):
    port_manager = PortManager([], {Operator.F_INIT: ["f_i"], Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    for _ in range(5):
        validator.reuse_instance()
        validator.check_receive("f_i", None)
        validator.check_receive("o_f", None)
    validator.reuse_instance()
    validator.check_receive("f_i", None)
    with pytest.raises(TestMMSFValidatorException):
        validator.reuse_instance()
    with pytest.raises(TestMMSFValidatorException):
        validator.check_receive("f_i", None)


def test_not_all_ports_used(mock_peer_info):
    port_manager = PortManager([], {
            Operator.F_INIT: ["f_i1", "f_i2"], Operator.O_F: ["o_f"]})
    port_manager.connect_ports(mock_peer_info)
    validator = MMSFValidator(port_manager)

    validator.reuse_instance()
    validator.check_receive("f_i1", None)
    with pytest.raises(TestMMSFValidatorException):
        validator.check_send("o_f", None)
