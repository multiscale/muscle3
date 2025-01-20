import pytest

from libmuscle.manager.deadlock_detector import DeadlockDetector


@pytest.fixture
def detector() -> DeadlockDetector:
    return DeadlockDetector()


def test_no_deadlock(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", None)
    assert not detector.is_deadlocked("macro")
    assert not detector.is_deadlocked("micro")
    detector.waiting_for_receive_done("macro", "micro", "s", None)
    assert not detector.is_deadlocked("macro")
    assert not detector.is_deadlocked("micro")


def test_double_waiting_log_error(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", 0)
    with pytest.raises(AssertionError):
        detector.waiting_for_receive("macro", "micro", "s", 1)


def test_not_waiting_log_error(detector: DeadlockDetector) -> None:
    with pytest.raises(AssertionError):
        detector.waiting_for_receive_done("macro", "micro", "s", 0)


def test_waiting_for_different_instance_log_error(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", 0)
    with pytest.raises(AssertionError):
        detector.waiting_for_receive_done("macro", "meso", "s", 0)


def test_waiting_for_different_port_log_error(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", 0)
    with pytest.raises(AssertionError):
        detector.waiting_for_receive_done("macro", "micro", "f_init", 0)


def test_deadlock(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", None)
    assert not detector.is_deadlocked("macro")
    assert not detector.is_deadlocked("micro")
    detector.waiting_for_receive("micro", "macro", "f_init", None)
    assert detector.is_deadlocked("macro")
    assert detector.is_deadlocked("micro")


def test_deadlock_cancelled(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", None)
    detector.waiting_for_receive("micro", "macro", "f_init", None)
    detector.waiting_for_receive_done("macro", "micro", "s", None)
    assert not detector.is_deadlocked("macro")
    assert not detector.is_deadlocked("micro")


def test_double_deadlock(detector: DeadlockDetector) -> None:
    detector.waiting_for_receive("macro", "micro", "s", None)
    detector.waiting_for_receive("micro", "macro", "f_init", None)
    detector.waiting_for_receive("cycle2", "peer2", "s", None)
    detector.waiting_for_receive("peer2", "cycle2", "f_init", None)
    detector.waiting_for_receive_done("macro", "micro", "s", None)
    assert not detector.is_deadlocked("macro")
    assert not detector.is_deadlocked("micro")
    assert detector.is_deadlocked("cycle2")
    assert detector.is_deadlocked("peer2")
