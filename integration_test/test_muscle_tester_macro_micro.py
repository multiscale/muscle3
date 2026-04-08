"""Integration tests for MuscleTester and ImplementationTester.

These tests verify that the MuscleTester and ImplementationTester work correctly
by testing the macro and micro components from the macro-micro example.

The macro model (integration_test/codes/macro):
  - Sends on port 'out' (O_I): integers 0, 1 for two iterations
  - Receives on port 'in' (S): expects the same integer back

The micro model (integration_test/codes/micro):
  - Receives on port 'init' (F_INIT)
  - Sends on port 'final' (O_F): echoes back the received value

When testing the micro model, the ImplementationTester acts as the macro:
  - It sends messages on 'init' and receives replies on 'final'.

When testing the macro model, the ImplementationTester acts as the micro:
  - It receives messages on 'out' and sends replies on 'in'.
"""
import os
from pathlib import Path

import pytest

from libmuscle import Message
from libmuscle.pytest import MuscleTester


YMMSL_CODES_DIR = Path(__file__).parent / 'ymmsl' / 'codes'
CODES_DIR = Path(__file__).parent / 'codes'


@pytest.fixture
def muscle3_tester(tmp_path: Path):
    """Pytest fixture providing a MuscleTester instance with a run directory."""
    run_dir = tmp_path / 'run_dir'
    run_dir.mkdir()
    with MuscleTester(run_dir) as tester:
        yield tester


@pytest.fixture(autouse=True)
def set_pythonpath():
    """Ensure the codes directory is on PYTHONPATH so 'python3 -m micro' works."""
    original = os.environ.get('PYTHONPATH', '')
    codes_path = str(CODES_DIR)
    if original:
        os.environ['PYTHONPATH'] = codes_path + ':' + original
    else:
        os.environ['PYTHONPATH'] = codes_path
    yield
    os.environ['PYTHONPATH'] = original


def test_micro_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Test the micro model using MuscleTester acting as the macro.

    The micro model:
      - Receives a value on 'init' (F_INIT)
      - Sends the same value back on 'final' (O_F)

    The tester (acting as macro):
      - Sends integers 0 and 1 on 'init'
      - Expects to receive the same integers back on 'final'
    """
    ymmsl_path = str(YMMSL_CODES_DIR / 'micro1.ymmsl')
    tester = muscle3_tester.start_implementation(ymmsl_path, 'micro1')

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
    ymmsl_path = str(YMMSL_CODES_DIR / 'macro.ymmsl')

    tester = muscle3_tester.start_implementation(ymmsl_path, 'macro')

    for i in range(2):
        msg = tester.receive('out')
        assert msg.data == i, (
            f"Iteration {i}: expected macro to send {i}, got {msg.data}"
        )

        reply = Message(msg.timestamp, msg.next_timestamp, msg.data)
        tester.send('in', reply)
