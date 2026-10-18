import threading
from unittest.mock import MagicMock

import pytest

from libmuscle import Message
from libmuscle.pytest.implementation_tester import (
    PARENT_SETTINGS_PORT_NAME,
    PARENT_TESTER_NAME,
    SIBLING_TESTER_NAME,
    ImplementationTester,
    _run_concurrently,
)
from libmuscle.timeline_manager import TimelineError

TIMEOUT = 5.0


def make_tester() -> ImplementationTester:
    """An ImplementationTester with mock parent and sibling instances."""
    tester = object.__new__(ImplementationTester)
    tester._default_timeout = TIMEOUT
    tester._is_shut_down = False
    tester._parent = MagicMock()
    tester._sibling = MagicMock()
    tester._parent_ports = {"init", "final"}
    tester._sibling_ports = {"in", "out"}
    tester._round_sent = set()
    return tester


def wait_for(event: threading.Event) -> None:
    """Wait for the event, failing instead of hanging if it doesn't come."""
    assert event.wait(TIMEOUT), "Timed out, tester instances do not run concurrently"


def fail() -> None:
    raise ValueError("Failed")


def test_run_concurrently() -> None:
    # Results and errors are collected per task
    results, errors = _run_concurrently({"ok": lambda: 1, "fail": fail})
    assert results == {"ok": 1}
    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)

    # A single task is run in the calling thread
    results, errors = _run_concurrently({"only": threading.current_thread})
    assert results == {"only": threading.current_thread()}
    assert errors == []

    results, errors = _run_concurrently({"only": fail})
    assert results == {}
    assert len(errors) == 1
    assert isinstance(errors[0], ValueError)


def test_cleanup() -> None:
    # The testers finish concurrently: each can only finish once the other started
    tester = make_tester()
    parent_started = threading.Event()
    sibling_started = threading.Event()

    def parent_reuse() -> bool:
        parent_started.set()
        wait_for(sibling_started)
        return False

    def sibling_reuse() -> bool:
        sibling_started.set()
        wait_for(parent_started)
        return False

    tester._parent.reuse_instance.side_effect = parent_reuse
    tester._sibling.reuse_instance.side_effect = sibling_reuse

    tester.cleanup()
    tester._parent.error_shutdown.assert_not_called()
    tester._sibling.error_shutdown.assert_not_called()

    # On an error, only the failing tester is shut down, and the error is raised
    tester = make_tester()
    tester._parent.reuse_instance.return_value = False
    tester._sibling.reuse_instance.side_effect = TimelineError("Not finished")

    with pytest.raises(TimelineError, match="Not finished"):
        tester.cleanup()
    tester._sibling.error_shutdown.assert_called_once_with("Not finished")
    tester._parent.error_shutdown.assert_not_called()

    # After shutting down because of an error, cleaning up does nothing
    tester = make_tester()
    tester._shut_down_all("Error")

    tester.cleanup()
    tester._parent.reuse_instance.assert_not_called()


def test_shut_down_all() -> None:
    # The testers shut down concurrently: each can only finish once the other shut down
    tester = make_tester()
    parent_started = threading.Event()
    sibling_started = threading.Event()

    def parent_shutdown(_: str) -> None:
        parent_started.set()
        wait_for(sibling_started)

    def sibling_shutdown(_: str) -> None:
        sibling_started.set()
        wait_for(parent_started)

    tester._parent.error_shutdown.side_effect = parent_shutdown
    tester._sibling.error_shutdown.side_effect = sibling_shutdown

    tester._shut_down_all("Error")

    assert tester._is_shut_down
    tester._parent.error_shutdown.assert_called_once_with("Error")
    tester._sibling.error_shutdown.assert_called_once_with("Error")


def test_send() -> None:
    # Sending again on an F_INIT port starts a new round, also for the sibling
    tester = make_tester()
    tester.send("init", Message(0.0, None, 0))
    tester.send("out", Message(0.0, None, 1))
    tester.send("init", Message(1.0, None, 2))

    assert tester._sibling.reuse_instance.call_count == 2
    tester._sibling.send.assert_called_once()

    # Each F_INIT port and slot is sent on once per round
    tester = make_tester()
    tester._parent_ports.add("init2")

    tester.send("init", Message(0.0, None, 0), 0)
    tester.send("init", Message(0.0, None, 0), 1)
    tester.send("init2", Message(0.0, None, 0))
    assert tester._sibling.reuse_instance.call_count == 1

    tester.send("init", Message(1.0, None, 1), 1)
    assert tester._sibling.reuse_instance.call_count == 2

    # Without a sibling, only the parent sends
    tester = make_tester()
    tester._sibling = None
    tester._sibling_ports = set()

    tester.send("init", Message(0.0, None, 0))
    tester.send("init", Message(1.0, None, 1))
    assert tester._parent.send.call_count == 2

    # muscle_settings_in is sent on through the parent's settings port
    tester = make_tester()
    tester._parent_ports.add(PARENT_SETTINGS_PORT_NAME)
    msg = Message(0.0, None, 0)

    tester.send("muscle_settings_in", msg)
    tester._parent.send.assert_any_call(PARENT_SETTINGS_PORT_NAME, msg, None)

    # Using a sibling port before F_INIT is an error, which shuts down all testers
    tester = make_tester()
    with pytest.raises(RuntimeError, match="before sending a message"):
        tester.send("out", Message(0.0, None, 0))
    assert tester._is_shut_down
    tester._sibling.send.assert_not_called()

    # Using an unknown port is an error, which lists the available ports and shuts
    # down all testers
    tester = make_tester()
    with pytest.raises(ValueError, match="Available ports are: final, in, init, out"):
        tester.send("nonexistent", Message(0.0, None, 0))
    assert tester._is_shut_down

    # An error while sending shuts down all testers
    tester = make_tester()
    tester._parent.send.side_effect = RuntimeError("Connection lost")

    with pytest.raises(RuntimeError, match="Connection lost"):
        tester.send("init", Message(0.0, None, 0))
    assert tester._is_shut_down
    tester._parent.error_shutdown.assert_called_once_with("Connection lost")
    tester._sibling.error_shutdown.assert_called_once_with("Connection lost")


def test_receive() -> None:
    # Using a sibling port before F_INIT is an error, which shuts down all testers
    tester = make_tester()
    with pytest.raises(RuntimeError, match="before sending a message"):
        tester.receive("in")
    assert tester._is_shut_down
    tester._sibling.receive.assert_not_called()

    # Using an unknown port is an error, which lists the available ports and shuts
    # down all testers
    tester = make_tester()
    with pytest.raises(ValueError, match="Available ports are: final, in, init, out"):
        tester.receive("nonexistent")
    assert tester._is_shut_down

    # An error while receiving shuts down all testers
    tester = make_tester()
    tester._parent.receive.side_effect = RuntimeError("Deadlock detected")

    with pytest.raises(RuntimeError, match="Deadlock detected"):
        tester.receive("final")
    assert tester._is_shut_down
    tester._parent.error_shutdown.assert_called_once_with("Deadlock detected")
    tester._sibling.error_shutdown.assert_called_once_with("Deadlock detected")


def test_create_instances(monkeypatch: pytest.MonkeyPatch) -> None:
    # If one Instance cannot be created, the others are shut down
    parent = MagicMock()

    def create_instance(name: str, *_: object) -> MagicMock:
        if name == SIBLING_TESTER_NAME:
            raise RuntimeError("Timeout waiting for peers to appear")
        return parent

    monkeypatch.setattr(
        ImplementationTester, "_create_instance", staticmethod(create_instance)
    )
    tester = object.__new__(ImplementationTester)
    programs = {PARENT_TESTER_NAME: MagicMock(), SIBLING_TESTER_NAME: MagicMock()}

    with pytest.raises(RuntimeError, match="Timeout waiting for peers"):
        tester._create_instances(programs, "tcp:localhost:9000")
    parent.error_shutdown.assert_called_once_with("Timeout waiting for peers to appear")
