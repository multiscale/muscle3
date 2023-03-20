import time
import pytest
from ymmsl import CheckpointRangeRule, CheckpointAtRule, Checkpoints

from libmuscle.checkpoint_triggers import (
    CombinedCheckpointTriggers, AtCheckpointTrigger, RangeCheckpointTrigger,
    TriggerManager)


def test_at_checkpoint_trigger():
    trigger = AtCheckpointTrigger([CheckpointAtRule([1.0, 3.0, 4.0, 4.5, 9.0])])

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
    range = CheckpointRangeRule(start=0.0, stop=20.0, every=1.2)
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
    range = CheckpointRangeRule(start=1.0, every=1.2)
    trigger = RangeCheckpointTrigger(range)

    assert trigger.next_checkpoint(-1.) == 1
    assert trigger.previous_checkpoint(-1.) is None

    assert trigger.next_checkpoint(148148.) == pytest.approx(148148.2)
    assert trigger.previous_checkpoint(148148.) == pytest.approx(148147)

    assert trigger.next_checkpoint(148148148.) == pytest.approx(148148149)
    assert trigger.previous_checkpoint(148148148.) == pytest.approx(148148147.8)


def test_range_checkpoint_trigger_default_start():
    range = CheckpointRangeRule(every=1.2, stop=10.0)
    trigger = RangeCheckpointTrigger(range)

    assert trigger.next_checkpoint(10) is None
    assert trigger.previous_checkpoint(10) == pytest.approx(9.6)

    assert trigger.next_checkpoint(0.0) == pytest.approx(1.2)
    assert trigger.previous_checkpoint(0.0) == pytest.approx(0.0)

    assert trigger.next_checkpoint(-148148.) == pytest.approx(-148147.2)
    assert trigger.previous_checkpoint(-148148.) == pytest.approx(-148148.4)


def test_combined_checkpoint_trigger_every_at():
    rules = [CheckpointRangeRule(every=10.0), CheckpointAtRule([3.0, 7.0, 13.0, 17.0])]
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
    rules = [CheckpointAtRule([3.0, 7.0, 13.0, 17.0]),
             CheckpointRangeRule(start=0.0, every=5.0, stop=20.0),
             CheckpointRangeRule(start=20.0, every=20.0, stop=100.0)]
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
    monotonic_start = time.monotonic()
    ref_elapsed = 15.0
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(ref_elapsed, Checkpoints(at_end=True))
    elapsed_walltime = trigger_manager.elapsed_walltime()
    duration = time.monotonic() - monotonic_start
    assert ref_elapsed < elapsed_walltime < (ref_elapsed + duration)


def test_trigger_manager():
    ref_elapsed = 0.0
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(ref_elapsed, Checkpoints(
            at_end=True,
            wallclock_time=[CheckpointAtRule([1e-12])],
            simulation_time=[CheckpointAtRule([1.0, 3.0, 5.0])]))

    assert trigger_manager.should_save_snapshot(0.1)
    triggers = trigger_manager.get_triggers()
    assert len(triggers) == 1
    assert "wallclock_time" in triggers[0]
    trigger_manager.update_checkpoints(0.1)

    assert not trigger_manager.should_save_snapshot(0.99)

    assert trigger_manager.should_save_snapshot(3.2)
    triggers = trigger_manager.get_triggers()
    assert len(triggers) == 1
    assert "simulation_time" in triggers[0]
    trigger_manager.update_checkpoints(3.2)

    assert trigger_manager.should_save_final_snapshot(True, 7.0)
    assert len(trigger_manager.get_triggers()) > 0
    trigger_manager.update_checkpoints(7.0)

    assert not trigger_manager.should_save_snapshot(7.1)

    assert trigger_manager.should_save_final_snapshot(False, None)
    trigger_manager.update_checkpoints(7.1)


def test_no_checkpointing() -> None:
    trigger_manager = TriggerManager()
    trigger_manager.set_checkpoint_info(0.0, Checkpoints())

    assert not trigger_manager.should_save_snapshot(1)
    assert not trigger_manager.should_save_snapshot(5000)
    assert not trigger_manager.should_save_final_snapshot(False, None)
