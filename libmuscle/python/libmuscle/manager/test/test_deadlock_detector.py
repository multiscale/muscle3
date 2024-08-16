import logging
import time
from typing import Iterator
from unittest.mock import Mock

import pytest

from libmuscle.manager.deadlock_detector import DeadlockDetector


@pytest.fixture
def shutdown_callback() -> Mock:
    return Mock()


@pytest.fixture
def detector(shutdown_callback) -> Iterator[DeadlockDetector]:
    # Using a very short delay (10ms) to speed up unit testing
    detector = DeadlockDetector(shutdown_callback, 0.01)
    detector.start()
    yield detector
    if detector.is_alive():
        detector.shutdown()
        detector.join()


def test_no_deadlock(shutdown_callback: Mock, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", None)
    detector.put_waiting_done("macro", "micro", "s", None)
    time.sleep(0.05)
    detector.shutdown()
    detector.join()
    shutdown_callback.assert_not_called()


def test_double_waiting_log_error(
        caplog: pytest.LogCaptureFixture, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", 0)
    detector.put_waiting("macro", "micro", "s", 1)
    detector.shutdown()
    detector.join()
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][:2] == (
            "libmuscle.manager.deadlock_detector", logging.ERROR)


def test_not_waiting_log_error(
        caplog: pytest.LogCaptureFixture, detector: DeadlockDetector) -> None:
    detector.put_waiting_done("macro", "micro", "s", 0)
    detector.shutdown()
    detector.join()
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][:2] == (
            "libmuscle.manager.deadlock_detector", logging.ERROR)


def test_waiting_for_different_instance_log_error(
        caplog: pytest.LogCaptureFixture, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", 0)
    detector.put_waiting_done("macro", "meso", "s", 0)
    detector.shutdown()
    detector.join()
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][:2] == (
            "libmuscle.manager.deadlock_detector", logging.ERROR)


def test_waiting_for_different_port_log_error(
        caplog: pytest.LogCaptureFixture, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", 0)
    detector.put_waiting_done("macro", "micro", "f_init", 0)
    detector.shutdown()
    detector.join()
    assert len(caplog.record_tuples) == 1
    assert caplog.record_tuples[0][:2] == (
            "libmuscle.manager.deadlock_detector", logging.ERROR)


def test_deadlock(shutdown_callback: Mock, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", None)
    detector.put_waiting("micro", "macro", "f_init", None)
    detector.join(1)  # wait max 1 second then check that the deadlock was detected
    assert not detector.is_alive()
    shutdown_callback.assert_called_once()


def test_deadlock_cancelled(
        shutdown_callback: Mock, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", None)
    detector.put_waiting("micro", "macro", "f_init", None)
    detector.put_waiting_done("macro", "micro", "s", None)
    time.sleep(0.05)
    detector.shutdown()
    detector.join()
    shutdown_callback.assert_not_called()


def test_double_deadlock(shutdown_callback: Mock, detector: DeadlockDetector) -> None:
    detector.put_waiting("macro", "micro", "s", None)
    detector.put_waiting("micro", "macro", "f_init", None)
    detector.put_waiting("cycle2", "peer2", "s", None)
    detector.put_waiting("peer2", "cycle2", "f_init", None)
    detector.put_waiting_done("macro", "micro", "s", None)
    detector.join(1)  # wait max 1 second then check that the deadlock was detected
    assert not detector.is_alive()
    shutdown_callback.assert_called()
