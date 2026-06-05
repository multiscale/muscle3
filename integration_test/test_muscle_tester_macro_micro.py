from pathlib import Path

import pytest

from libmuscle import Message
from libmuscle.pytest import MuscleTester


YMMSL_CODES_DIR = Path(__file__).parent / 'ymmsl' / 'codes'
CODES_DIR = Path(__file__).parent / 'codes'


@pytest.fixture(autouse=True)
def set_pythonpath(monkeypatch):
    """Ensure the codes directory is on PYTHONPATH so 'python3 -m micro' works."""
    monkeypatch.setenv("PYTHONPATH", str(CODES_DIR),  prepend=":")


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
        YMMSL_CODES_DIR / 'micro1.ymmsl','micro1'
        )

    for i in range(2):
        msg = Message(float(i) * 10.0, float(i + 1) * 10.0, i)

        tester.send('init', msg)
        reply = tester.receive('final')

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
        YMMSL_CODES_DIR / 'macro.ymmsl', 'macro'
        )

    for i in range(2):
        msg = tester.receive('out')
        assert msg.data == i, (
            f"Iteration {i}: expected macro to send {i}, got {msg.data}"
        )

        reply = Message(msg.timestamp, msg.next_timestamp, msg.data)
        tester.send('in', reply)


def test_receive_timeout_raises_error(muscle3_tester: MuscleTester) -> None:
    """Test that a RuntimeError is raised when the tester's receive times out.

    The tester tries to receive on 'final' without first sending on 'init'. The micro
    model is blocked waiting to receive on 'init', so it never sends on 'final', and
    the tester's receive will time out and raise a RuntimeError.
    """
    tester = muscle3_tester.start_implementation(
        YMMSL_CODES_DIR / 'micro1.ymmsl', 'micro1', default_timeout=0.1
    )

    with pytest.raises(RuntimeError):
        tester.receive('final')
