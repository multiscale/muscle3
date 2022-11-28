import bisect
from datetime import datetime, timezone
import logging
import os
import time
from typing import List, Optional, Union

from ymmsl import (
        CheckpointRangeRule, CheckpointAtRule, CheckpointRule, Checkpoints)


_logger = logging.getLogger(__name__)


def _checkpoint_error(description: str) -> None:
    if "MUSCLE_DISABLE_CHECKPOINT_ERRORS" in os.environ:
        _logger.warning(f"Suppressed checkpoint error: {description}")
    else:
        raise RuntimeError(description)


class CheckpointTrigger:
    """Represents a trigger for creating snapshots"""

    def next_checkpoint(self, cur_time: float) -> Optional[float]:
        """Calculate the next checkpoint time

        Args:
            cur_time: current time.

        Returns:
            The time when a next checkpoint should be taken, or None if this
            trigger has no checkpoint after cur_time.
        """
        raise NotImplementedError()

    def previous_checkpoint(self, cur_time: float) -> Optional[float]:
        """Calculate the previous checkpoint time

        Args:
            cur_time: current time.

        Returns:
            The time when a previous checkpoint should have been taken, or None
            if this trigger has no checkpoint after cur_time.
        """
        raise NotImplementedError()


class AtCheckpointTrigger(CheckpointTrigger):
    """Represents a trigger based on an "at" checkpoint rule

    This triggers at the specified times.
    """

    def __init__(self, at_rules: List[CheckpointAtRule]) -> None:
        """Create an "at" checkpoint trigger

        Args:
            at: list of checkpoint moments
        """
        self._at = []
        for at_rule in at_rules:
            self._at.extend(at_rule.at)
        self._at.sort()

    def next_checkpoint(self, cur_time: float) -> Optional[float]:
        if cur_time >= self._at[-1]:
            return None  # no future checkpoint left
        idx = bisect.bisect(self._at, cur_time)
        return self._at[idx]

    def previous_checkpoint(self, cur_time: float) -> Optional[float]:
        if cur_time < self._at[0]:
            return None  # no previous checkpoint
        idx = bisect.bisect(self._at, cur_time)
        return self._at[idx - 1]


class RangeCheckpointTrigger(CheckpointTrigger):
    """Represents a trigger based on a "ranges" checkpoint rule

    This triggers at a range of checkpoint moments.

    Equivalent an "at" rule ``[start, start + step, start + 2*step, ...]`` for
    as long as ``start + i*step <= stop``.

    Stop may be omitted, in which case the range is infinite.

    Start may be omitted, in which case the range is equivalent to an "at" rule
    ``[..., -n*step, ..., -step, 0, step, 2*step, ...]`` for as long as
    ``i*step <= stop``.

    Note: the "every" rule is a special case of a range with start and stop
    omitted, and is handled by this class as well
    """

    def __init__(self, range: CheckpointRangeRule) -> None:
        """Create a range of checkpoints

        Args:
            range: checkpoint range defining start, stop and step.
        """
        self._start = range.start
        self._stop = range.stop
        self._every = range.every
        self._last = None  # type: Union[int, float, None]
        if self._stop is not None:
            start = 0 if self._start is None else self._start
            diff = self._stop - start
            self._last = start + (diff // self._every) * self._every

    def next_checkpoint(self, cur_time: float) -> Optional[float]:
        if self._start is not None and cur_time < self._start:
            return float(self._start)
        if self._last is not None and cur_time >= self._last:
            return None
        start = 0 if self._start is None else self._start
        diff = cur_time - start
        return float(start + (diff // self._every + 1) * self._every)

    def previous_checkpoint(self, cur_time: float) -> Optional[float]:
        if self._start is not None and cur_time < self._start:
            return None
        if self._last is not None and cur_time > self._last:
            return float(self._last)
        start = 0 if self._start is None else self._start
        diff = cur_time - start
        return float(start + (diff // self._every) * self._every)


class CombinedCheckpointTriggers(CheckpointTrigger):
    """Checkpoint trigger based on a combination of "every", "at" and "ranges"
    """

    def __init__(self, checkpoint_rules: List[CheckpointRule]) -> None:
        """Create a new combined checkpoint trigger from the given rules

        Args:
            checkpoint_rules: checkpoint rules (from ymmsl)
        """
        self._triggers = []     # type: List[CheckpointTrigger]
        at_rules = []           # type: List[CheckpointAtRule]
        for rule in checkpoint_rules:
            if isinstance(rule, CheckpointAtRule):
                if rule.at:
                    at_rules.append(rule)
            elif isinstance(rule, CheckpointRangeRule):
                self._triggers.append(RangeCheckpointTrigger(rule))
            else:
                raise RuntimeError('Unknown checkpoint rule')
        if at_rules:
            self._triggers.append(AtCheckpointTrigger(at_rules))

    def next_checkpoint(self, cur_time: float) -> Optional[float]:
        checkpoints = (trigger.next_checkpoint(cur_time)
                       for trigger in self._triggers)
        # return earliest of all not-None next-checkpoints
        return min((checkpoint
                    for checkpoint in checkpoints
                    if checkpoint is not None),
                   default=None)  # return None if all triggers return None

    def previous_checkpoint(self, cur_time: float) -> Optional[float]:
        checkpoints = (trigger.previous_checkpoint(cur_time)
                       for trigger in self._triggers)
        # return latest of all not-None previous-checkpoints
        return max((checkpoint
                    for checkpoint in checkpoints
                    if checkpoint is not None),
                   default=None)  # return None if all triggers return None


def _utc_to_monotonic(utc: datetime) -> float:
    """Convert UTC time point to a reference value of time.monotonic()

    Args:
        utc: datetime in UTC timezone
    """
    curmono = time.monotonic()
    curutc = datetime.now(timezone.utc)
    elapsed_seconds = (curutc - utc).total_seconds()
    return curmono - elapsed_seconds


class TriggerManager:
    """Manages all checkpoint triggers and checks if a snapshot must be saved.
    """

    def __init__(self) -> None:
        self._has_checkpoints = False
        self._last_triggers = []    # type: List[str]
        self._monotonic_reference = time.monotonic()

    def set_checkpoint_info(
            self, utc_reference: datetime, checkpoints: Checkpoints) -> None:
        """Register checkpoint info received from the muscle manager.
        """
        if not checkpoints:
            self._has_checkpoints = False
            return

        self._has_checkpoints = True
        self._monotonic_reference = _utc_to_monotonic(utc_reference)

        self._checkpoint_at_end = checkpoints.at_end

        self._wall = CombinedCheckpointTriggers(checkpoints.wallclock_time)
        self._prevwall = 0.0
        self._nextwall = self._wall.next_checkpoint(0.0)  # type: Optional[float]

        self._sim = CombinedCheckpointTriggers(checkpoints.simulation_time)
        self._prevsim = None        # type: Optional[float]
        self._nextsim = None        # type: Optional[float]
        self._sim_reset = True

        self._first_reuse = True

        # These attributes are only used to check if implementations are
        # following the guidelines
        self._should_have_saved = False
        self._should_save_final_called = False
        self._saved_final_checkpoint = False

    def elapsed_walltime(self) -> float:
        """Returns elapsed wallclock_time in seconds.
        """
        return time.monotonic() - self._monotonic_reference

    def snapshots_enabled(self) -> bool:
        """Check if the current workflow has snapshots enabled.
        """
        return self._has_checkpoints

    def should_save_snapshot(self, timestamp: float) -> bool:
        """Handles instance.should_save_snapshot
        """
        if not self._has_checkpoints:
            return False

        self.__check_should_have_saved()

        elapsed_walltime = self.elapsed_walltime()
        value = self.__should_save(elapsed_walltime, timestamp)
        self._should_have_saved = value
        return value

    def should_save_final_snapshot(
            self, do_reuse: bool, f_init_max_timestamp: Optional[float]
            ) -> bool:
        """Handles instance.should_save_final_snapshot
        """
        if not self._has_checkpoints:
            return False

        self.__check_should_have_saved()

        value = False
        if not do_reuse and self._checkpoint_at_end:
            value = True
            self._last_triggers.append('at_end')
        elif f_init_max_timestamp is None:
            # No F_INIT messages received: reuse triggered on muscle_settings_in
            # message.
            _logger.debug('Reuse triggered by muscle_settings_in.'
                          ' Not creating a snapshot.')
            self._sim_reset = True
        else:
            elapsed_walltime = self.elapsed_walltime()
            value = self.__should_save(elapsed_walltime, f_init_max_timestamp)

        self._should_have_saved = value
        self._should_save_final_called = True
        return value

    @property
    def save_final_snapshot_called(self) -> bool:
        """Check if :meth:`save_final_snapshot` was called during this
        reuse loop.
        """
        return self._saved_final_checkpoint

    def reuse_instance(self) -> None:
        """Cleanup between instance reuse
        """
        if not self._has_checkpoints:
            return
        if self._first_reuse:
            self._first_reuse = False
        else:
            if self._should_have_saved:
                _checkpoint_error('"should_save_snapshot" or '
                                  '"should_save_final_snapshot" returned'
                                  ' positive but no snapshot was saved before'
                                  ' exiting the reuse loop.')
            if not (self._should_save_final_called or self._saved_final_checkpoint):
                _checkpoint_error('You must call "should_save_final" exactly'
                                  ' once in the reuse loop of an instance that'
                                  ' supports checkpointing.')
        self._should_save_final_called = False
        self._saved_final_checkpoint = False

    def update_checkpoints(self, timestamp: float, final: bool) -> None:
        """Update last and next checkpoint times when a snapshot is made.

        Args:
            timestamp: timestamp as reported by the instance (or from incoming
                F_INIT messages when final=True).
            final: True iff this is coming from a save_final_snapshot call.
        """
        if not self._has_checkpoints:
            _logger.info('Saving a snapshot but no checkpoints requested by the'
                         ' workflow. Hint: use Instance.should_save_snapshot(),'
                         ' Instance.should_save_final_snapshot() or'
                         ' Instance.snapshots_enabled() to test if it is useful'
                         ' to save a snapshot.')
            return
        if final and self._saved_final_checkpoint:
            raise RuntimeError(
                    'You may only save a final snapshot once per reuse loop.')

        self._prevwall = self.elapsed_walltime()
        self._nextwall = self._wall.next_checkpoint(self._prevwall)

        self._prevsim = timestamp
        self._nextsim = self._sim.next_checkpoint(timestamp)

        # this method is also called during resume, after which we no longer
        # consider the simulation_time as reset
        self._sim_reset = False
        self._should_have_saved = False
        self._saved_final_checkpoint = final

    def get_triggers(self) -> List[str]:
        """Get trigger description(s) for the current reason for checkpointing.
        """
        triggers = self._last_triggers
        self._last_triggers = []
        return triggers

    def __check_should_have_saved(self) -> None:
        """Check if a snapshot is saved when required."""
        if self._should_have_saved:
            _checkpoint_error('"should_save_snapshot" or '
                              '"should_save_final_snapshot" returned positive'
                              ' but no snapshot was saved before the next call'
                              ' to a should_save_ method.'
                              ' You must call the corresponding save_snapshot'
                              ' or save_final_snapshot method when should_save_'
                              ' returns True.')

    def __should_save(self, walltime: float, simulation_time: float) -> bool:
        """Check if a checkpoint should be taken

        Args:
            walltime: current wallclock time (elapsed since reference)
            simulation_time: current/next timestamp as reported by the instance
        """
        if self._sim_reset:
            # we cannot make assumptions about the start time of a simulation,
            # a t=-1000 could make sense if t represents years since CE
            # and we should not disallow checkpointing for negative t
            previous = self._sim.previous_checkpoint(simulation_time)
            if previous is not None:
                # there is a checkpoint rule before the current moment, assume
                # we should have taken a snapshot back then
                self._nextsim = previous
            else:
                self._nextsim = self._sim.next_checkpoint(simulation_time)
            self._sim_reset = False

        self._last_triggers = []
        if self._nextwall is not None and walltime >= self._nextwall:
            self._last_triggers.append(f"wallclock_time >= {self._nextwall}")
        if self._nextsim is not None and simulation_time >= self._nextsim:
            self._last_triggers.append(f"simulation_time >= {self._nextsim}")
        return bool(self._last_triggers)
