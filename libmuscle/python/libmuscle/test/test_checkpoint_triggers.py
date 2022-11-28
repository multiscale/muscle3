from datetime import datetime, timedelta, timezone
import logging
import time
import pytest
from ymmsl import CheckpointRangeRule, CheckpointAtRule, Checkpoints

from libmuscle.checkpoint_triggers import (
    CombinedCheckpointTriggers, AtCheckpointTrigger, RangeCheckpointTrigger,
    TriggerManager)


def test_at_checkpoint_trigger():
    trigger = AtCheckpointTrigger([CheckpointAtRule([1, 3, 4, 4.5, 9])])

    assert trigger.next_checkpoint(0) == 1
    assert trigger.previous_checkpoint(0) is None

    assert trigger.next_checkpoint(1) == 3
    assert trigger.previous_checkpoint(1) == 1

    eps = 1e-16
    assert trigger.next_checkpoint(1 - eps) == 1
    assert trigger.previous_checkpoint(1 - eps) is None

    assert trigger.next_checkpoint(3.9) == 4
    assert trigger.previous_checkpoint(3.9) == 3

    assert trigger.next_checkpoint(4.1) == 4.5
    assert trigger.previous_checkpoint(4.1) == 4

    assert trigger.next_checkpoint(5) == 9
    assert trigger.previous_checkpoint(5) == 4.5

    assert trigger.next_checkpoint(9) is None
    assert trigger.previous_checkpoint(9) == 9

    assert trigger.next_checkpoint(11) is None
    assert trigger.previous_checkpoint(11) == 9


def test_range_checkpoint_trigger():
    range = CheckpointRangeRule(start=0, stop=20, every=1.2)
    trigger = RangeCheckpointTrigger(range)

    assert trigger.next_checkpoint(-1) == 0
    assert trigger.previous_checkpoint(-1) is None

    assert trigger.next_checkpoint(0) == pytest.approx(1.2)
    assert trigger.previous_checkpoint(0) == 0

    assert trigger.next_checkpoint(8) == pytest.approx(8.4)
    assert trigger.previous_checkpoint(8) == pytest.approx(7.2)

    assert trigger.next_checkpoint(18.2) == pytest.approx(19.2)
    assert trigger.previous_checkpoint(18.2) == pytest.approx(18)

    assert trigger.next_checkpoint(20) is None
    assert trigger.previous_checkpoint(20) == pytest.approx(19.2)


def test_range_checkpoint_trigger_default_stop():
    range = CheckpointRangeRule(start=1, every=1.2)
    trigger = RangeCheckpointTrigger(range)

    assert trigger.next_checkpoint(-1.) == 1
    assert trigger.previous_checkpoint(-1.) is None

    assert trigger.next_checkpoint(148148.) == pytest.approx(148148.2)
    assert trigger.previous_checkpoint(148148.) == pytest.approx(148147)

    assert trigger.next_checkpoint(148148148.) == pytest.approx(148148149)
    assert trigger.previous_checkpoint(148148148.) == pytest.approx(148148147.8)


def test_range_checkpoint_trigger_default_start():
    range = CheckpointRangeRule(every=1.2, stop=10)
    trigger = RangeCheckpointTrigger(range)

    assert trigger.next_checkpoint(10) is None
    assert trigger.previous_checkpoint(10) == pytest.approx(9.6)

    assert trigger.next_checkpoint(0.0) == pytest.approx(1.2)
    assert trigger.previous_checkpoint(0.0) == pytest.approx(0.0)

    assert trigger.next_checkpoint(-148148.) == pytest.approx(-148147.2)
    assert trigger.previous_checkpoint(-148148.) == pytest.approx(-148148.4)


def test_combined_checkpoint_trigger_every_at():
    rules = [CheckpointRangeRule(every=10), CheckpointAtRule([3, 7, 13, 17])]
    trigger = CombinedCheckpointTriggers(rules)

    assert trigger.next_checkpoint(-11.) == pytest.approx(-10)
    assert trigger.previous_checkpoint(-11) == pytest.approx(-20)

    assert trigger.next_checkpoint(0.) == pytest.approx(3)
    assert trigger.previous_checkpoint(0.) == pytest.approx(0)

    assert trigger.next_checkpoint(8.3) == pytest.approx(10)
    assert trigger.previous_checkpoint(8.3) == pytest.approx(7)

    assert trigger.next_checkpoint(14.2) == pytest.approx(17)
    assert trigger.previous_checkpoint(14.2) == pytest.approx(13)

    assert trigger.next_checkpoint(25.2) == pytest.approx(30)
    assert trigger.previous_checkpoint(25.2) == pytest.approx(20)


def test_combined_checkpoint_trigger_at_ranges():
    rules = [CheckpointAtRule([3, 7, 13, 17]),
             CheckpointRangeRule(start=0, every=5, stop=20),
             CheckpointRangeRule(start=20, every=20, stop=100)]
    trigger = CombinedCheckpointTriggers(rules)

    assert trigger.next_checkpoint(-11.) == pytest.approx(0)
    assert trigger.previous_checkpoint(-11) is None

    assert trigger.next_checkpoint(0.) == pytest.approx(3)
    assert trigger.previous_checkpoint(0.) == pytest.approx(0)

    assert trigger.next_checkpoint(8.3) == pytest.approx(10)
    assert trigger.previous_checkpoint(8.3) == pytest.approx(7)

    assert trigger.next_checkpoint(14.2) == pytest.approx(15)
    assert trigger.previous_checkpoint(14.2) == pytest.approx(13)

    assert trigger.next_checkpoint(19.3) == pytest.approx(20)
    assert trigger.previous_checkpoint(19.3) == pytest.approx(17)

    assert trigger.next_checkpoint(25.2) == pytest.approx(40)
    assert trigger.previous_checkpoint(25.2) == pytest.approx(20)

    assert trigger.next_checkpoint(95.2) == pytest.approx(100)
    assert trigger.previous_checkpoint(95.2) == pytest.approx(80)

    assert trigger.next_checkpoint(125.2) is None
    assert trigger.previous_checkpoint(125.2) == pytest.approx(100)


def test_trigger_manager_reference_time():
    monotonic_now = time.monotonic()
    utcnow = datetime.now(timezone.utc)
    reference = utcnow - timedelta(seconds=15)
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(reference, Checkpoints(at_end=True))
    elapsed_walltime = trigger_manager.elapsed_walltime()
    elapsed_monotonic = time.monotonic() - monotonic_now
    assert 15.0 < elapsed_walltime <= (15.0 + elapsed_monotonic)


def test_trigger_manager():
    reference = datetime.now(timezone.utc)
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(reference, Checkpoints(
            at_end=True,
            wallclock_time=[CheckpointAtRule([1e-12])],
            simulation_time=[CheckpointAtRule([1, 3, 5])]))

    trigger_manager.reuse_instance()

    assert trigger_manager.should_save_snapshot(0.1)
    triggers = trigger_manager.get_triggers()
    assert len(triggers) == 1
    assert "wallclock_time" in triggers[0]
    with pytest.raises(RuntimeError):  # did not call save in between
        trigger_manager.should_save_snapshot(0.1)
    trigger_manager.update_checkpoints(0.1, False)

    assert not trigger_manager.should_save_snapshot(0.99)

    assert trigger_manager.should_save_snapshot(3.2)
    triggers = trigger_manager.get_triggers()
    assert len(triggers) == 1
    assert "simulation_time" in triggers[0]
    trigger_manager.update_checkpoints(3.2, False)

    assert trigger_manager.should_save_final_snapshot(True, 7.0)
    with pytest.raises(RuntimeError):  # did not call save in between
        trigger_manager.should_save_snapshot(4.0)
    with pytest.raises(RuntimeError):  # did not call save in between
        trigger_manager.should_save_final_snapshot(True, 7.0)
    assert len(trigger_manager.get_triggers()) > 0
    trigger_manager.update_checkpoints(7.0, True)

    trigger_manager.reuse_instance()

    assert not trigger_manager.should_save_snapshot(7.1)
    with pytest.raises(RuntimeError):  # no should_save_final called
        trigger_manager.reuse_instance()

    assert trigger_manager.should_save_final_snapshot(False, None)
    with pytest.raises(RuntimeError):  # not saved
        trigger_manager.reuse_instance()
    trigger_manager.update_checkpoints(7.1, True)

    trigger_manager.reuse_instance()


def test_trigger_manager_warnings(caplog: pytest.LogCaptureFixture,
                                  monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MUSCLE_DISABLE_CHECKPOINT_ERRORS", "1")

    reference = datetime.now(timezone.utc)
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(reference, Checkpoints(
            simulation_time=[CheckpointAtRule([1, 3, 5])]))

    trigger_manager.reuse_instance()

    with caplog.at_level(logging.WARN):
        n_records = len(caplog.records)
        assert trigger_manager.should_save_snapshot(1.5)
        assert len(caplog.records) == n_records

        trigger_manager.reuse_instance()  # suppressed error
        assert len(caplog.records) > n_records
        assert "Suppressed checkpoint error" in caplog.records[-1].message