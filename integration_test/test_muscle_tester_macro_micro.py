import time
from pathlib import Path

import pytest

from libmuscle import Message
from libmuscle.mcp.tcp_transport_client import RECONNECT_TIMEOUT
from libmuscle.mmp_client import PEER_TIMEOUT
from libmuscle.pytest import MuscleTester

YMMSL_CODES_DIR = Path(__file__).parent / "ymmsl" / "codes"
CODES_DIR = Path(__file__).parent / "codes"


@pytest.fixture(autouse=True)
def set_pythonpath(monkeypatch):
    """Ensure the codes directory is on PYTHONPATH so 'python3 -m micro' works."""
    monkeypatch.setenv("PYTHONPATH", str(CODES_DIR), prepend=":")


def test_micro_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Test the micro model using MuscleTester acting as the macro.

    The micro model:
      - Receives a value on 'init' (F_INIT)
      - Sends the same value back on 'final' (O_F)

    The tester (acting as macro):
      - Sends integers 0 and 1 on 'init'
      - Expects to receive the same integers back on 'final'
    """
    tester = muscle3_tester.start_implementation(
        YMMSL_CODES_DIR / "micro1.ymmsl", "micro1"
    )

    for i in range(2):
        msg = Message(float(i) * 10.0, float(i + 1) * 10.0, i)

        tester.send("init", msg)
        reply = tester.receive("final")

        assert reply.data == i, (
            f"Iteration {i}: expected micro to echo back {i}, got {reply.data}"
        )
        assert reply.timestamp == float(i) * 10.0, (
            f"Iteration {i}: expected timestamp {float(i) * 10.0}, "
            f"got {reply.timestamp}"
        )


def test_macro_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Test the macro model using MuscleTester acting as the micro.

    The macro model:
      - Sends integers 0 and 1 on 'out' (O_I) for two iterations
      - Receives a reply on 'in' (S) and asserts it equals the sent integer

    The tester (acting as micro):
      - Receives messages on 'out'
      - Sends the same value back on 'in'
    """
    tester = muscle3_tester.start_implementation(
        YMMSL_CODES_DIR / "macro.ymmsl", "macro"
    )

    for i in range(2):
        msg = tester.receive("out")
        assert msg.data == i, (
            f"Iteration {i}: expected macro to send {i}, got {msg.data}"
        )

        reply = Message(msg.timestamp, msg.next_timestamp, msg.data)
        tester.send("in", reply)


def test_meso_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Test the meso model using MuscleTester acting as both its macro and its peer.

    The meso model has F_INIT and O_F ports, and O_I and S ports on two timelines.
    On each reuse loop iteration, it:
      - Receives an integer x on 'init' (F_INIT)
      - Sends x and x + 1 on 'out' (O_I), receiving a reply on 'in' (S) each time
      - Receives an integer y on 'in1' (S) and then sends x + y on 'out1' (O_I), twice
        (timeline sub1)
      - Sends the sum of all integers received on 'in' and 'in1' on 'final' (O_F)

    The tester mirrors this order.
    """
    tester = muscle3_tester.start_implementation(YMMSL_CODES_DIR / "meso.ymmsl", "meso")

    for x in (0, 10):
        tester.send("init", Message(float(x), None, x))

        # Default timeline: the implementation sends first
        for i in range(2):
            msg = tester.receive("out")
            assert msg.data == x + i
            tester.send("in", Message(msg.timestamp, None, 2 * msg.data))

        # Timeline sub1: the implementation receives first
        for y in (1, 2):
            tester.send("in1", Message(float(x), None, y))
            msg = tester.receive("out1")
            assert msg.data == x + y

        reply = tester.receive("final")
        assert reply.data == 2 * x + 2 * (x + 1) + 1 + 2


def test_unfinished_exchange_raises_error_on_cleanup(tmp_path: Path) -> None:
    """Test that cleaning up raises an error if the test did not finish an exchange,
    while still shutting down both tester components.
    """
    with pytest.raises(RuntimeError, match="Not allowed to call reuse_instance"):
        with MuscleTester(tmp_path / "run_dir") as muscle3_tester:
            tester = muscle3_tester.start_implementation(
                YMMSL_CODES_DIR / "meso.ymmsl", "meso", default_timeout=2.0
            )
            tester.send("init", Message(0.0, None, 0))
            tester.receive("out")


def test_receive_timeout_raises_error(muscle3_tester: MuscleTester) -> None:
    """Test that a RuntimeError is raised when the tester's receive times out.

    The tester tries to receive on 'final' without first sending on 'init'. The micro
    model is blocked waiting to receive on 'init', so it never sends on 'final', and
    the tester's receive will time out and raise a RuntimeError.
    """
    tester = muscle3_tester.start_implementation(
        YMMSL_CODES_DIR / "micro1.ymmsl", "micro1", default_timeout=2.0
    )

    with pytest.raises(RuntimeError):
        tester.receive("final")


def test_failing_actor(muscle3_tester: MuscleTester) -> None:
    """Test that a RuntimeError is raised when the actor crashes after registering.

    The test_program registers with MUSCLE3 using start_implementation, then crashes.
    Any subsequent communication attempt should raise a RuntimeError. This RuntimeError
    should be raised in at least min(RECONNECT_TIMEOUT, default_timeout) seconds.
    """
    default_timeout = 1.0
    tester = muscle3_tester.start_implementation(
        """
        ymmsl_version: v0.2
        programs:
          test_program:
            ports:
              o_f: output
            executable: python
            args: -c "import libmuscle;i=libmuscle.Instance();i.reuse_instance();1/0"
        """,
        "test_program",
        default_timeout=default_timeout,
    )

    start = time.monotonic()
    with pytest.raises(RuntimeError):
        tester.receive("output")
    elapsed = time.monotonic() - start

    eps = 5
    max_allowed_time = min(RECONNECT_TIMEOUT, default_timeout) + eps
    assert elapsed <= max_allowed_time, (
        f"Expected reconnection retries to take at most {max_allowed_time:.1f} s "
        f"(including {eps}s eps), but it took {elapsed:.1f} s"
    )


def test_failing_executable(muscle3_tester: MuscleTester) -> None:
    """Test that a RuntimeError is raised within default_timeout seconds when the
    executable does not exist and therefore never registers with the manager.

    Because the tester component cannot connect to its peer (which never starts),
    start_implementation itself should raise a RuntimeError after at most
    default_timeout seconds.
    """
    default_timeout = 1.0

    start = time.monotonic()
    with pytest.raises(RuntimeError, match="Could not connect to the implementation"):
        muscle3_tester.start_implementation(
            """
            ymmsl_version: v0.2
            programs:
              test_program:
                ports:
                  o_f: output
                executable: pythonX
            """,
            "test_program",
            default_timeout=default_timeout,
        )
    elapsed = time.monotonic() - start

    eps = 5
    max_allowed_time = min(PEER_TIMEOUT, default_timeout) + eps
    assert elapsed <= max_allowed_time, (
        f"Expected start_implementation to raise within {max_allowed_time:.1f} s "
        f"(including {eps}s eps), but it took {elapsed:.1f} s"
    )
