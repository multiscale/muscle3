"""Integration tests for MuscleTester and ImplementationTester.

These tests verify that the MuscleTester and ImplementationTester work correctly
by testing the macro and micro components from the macro-micro example.

The macro model (integration_test/codes/macro):
  - Sends on port 'out' (O_I)
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
    """Ensure example code directory is available for module resolution."""
    original = os.environ.get('PYTHONPATH', '')
    codes_path = str(CODES_DIR)
    os.environ['PYTHONPATH'] = codes_path + (':' + original if original else '')
    yield
    os.environ['PYTHONPATH'] = original


def test_micro_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Validate micro model integration via a single end-to-end message exchange.

    This test ensures:
    - The micro implementation starts correctly under MuscleTester
    - Messages sent on 'init' are received and processed
    - The response is correctly emitted on 'final'
    - Data integrity is preserved through the full IPC pipeline
    """
    ymmsl_path = str(YMMSL_CODES_DIR / 'micro1.ymmsl')
    tester = muscle3_tester.start_implementation(ymmsl_path, 'micro1')

    msg = Message(10.0, 20.0, 42)

    tester.send('init', msg)
    reply = tester.receive('final')

    assert reply.data == 42
    assert reply.timestamp == 10.0


def test_macro_model_with_tester(muscle3_tester: MuscleTester) -> None:
    """Validate macro model integration via a single end-to-end message exchange.

    This test ensures:
    - The macro implementation starts correctly under MuscleTester
    - A message is emitted on 'out'
    - The tester can respond on 'in'
    - The communication cycle between macro and tester is correctly wired
    """
    ymmsl_path = str(YMMSL_CODES_DIR / 'macro.ymmsl')
    tester = muscle3_tester.start_implementation(ymmsl_path, 'macro')

    msg = tester.receive('out')

    assert msg.data == 0

    reply = Message(msg.timestamp, msg.next_timestamp, msg.data)
    tester.send('in', reply)
