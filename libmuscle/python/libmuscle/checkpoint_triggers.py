import bisect
import logging
import time
from typing import List, Optional, Union

from ymmsl import (
        CheckpointRangeRule, CheckpointAtRule, CheckpointRule, Checkpoints)


_logger = logging.getLogger(__name__)


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
        self._at = sorted([a for r in at_rules for a in r.at])

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
    """

    def __init__(self, range: CheckpointRangeRule) -> None:
        """Create a range of checkpoints

        Args:
            range: checkpoint range defining start, stop and step.
        """
        self._start = range.start
        self._stop = range.stop
        self._every = range.every
        self._last: Union[int, float, None] = None
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
    """Checkpoint trigger based on a combination of "at" and "ranges"
    """

    def __init__(self, checkpoint_rules: List[CheckpointRule]) -> None:
        """Create a new combined checkpoint trigger from the given rules

        Args:
            checkpoint_rules: checkpoint rules (from ymmsl)
        """
        self._triggers: List[CheckpointTrigger] = []
        at_rules: List[CheckpointAtRule] = []
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


class TriggerManager:
    """Manages all checkpoint triggers and checks if a snapshot must be saved.
    """

    def __init__(self) -> None:
        self._has_checkpoints = False
        self._last_triggers: List[str] = []
        self._cpts_considered_until = float('-inf')

    def set_checkpoint_info(
            self, elapsed: float, checkpoints: Checkpoints) -> None:
        """Register checkpoint info received from the muscle manager.
        """
        self._mono_to_elapsed = elapsed - time.monotonic()

        if not checkpoints:
            self._has_checkpoints = False
            return

        self._has_checkpoints = True

        self._checkpoint_at_end = checkpoints.at_end

        self._wall = CombinedCheckpointTriggers(checkpoints.wallclock_time)
        self._prevwall = 0.0
        self._nextwall: Optional[float] = self._wall.next_checkpoint(0.0)

        self._sim = CombinedCheckpointTriggers(checkpoints.simulation_time)
        self._prevsim: Optional[float] = None
        self._nextsim: Optional[float] = None

    def elapsed_walltime(self) -> float:
        """Returns elapsed wallclock_time in seconds.
        """
        return time.monotonic() + self._mono_to_elapsed

    def checkpoints_considered_until(self) -> float:
        """Return elapsed time of last should_save*
        """
        return self._cpts_considered_until

    def harmonise_wall_time(self, at_least: float) -> None:
        """Ensure our elapsed time is at least the given value
        """
        cur = self.elapsed_walltime()
        if cur < at_least:
            _logger.debug(
                    'Harmonise wall time: advancing clock by %f seconds',
                    at_least - cur)
            self._mono_to_elapsed += at_least - cur

    def should_save_snapshot(self, timestamp: float) -> bool:
        """Handles instance.should_save_snapshot
        """
        if not self._has_checkpoints:
            return False

        return self.__should_save(timestamp)

    def should_save_final_snapshot(
            self, do_reuse: bool, f_init_max_timestamp: Optional[float]
            ) -> bool:
        """Handles instance.should_save_final_snapshot
        """
        if not self._has_checkpoints:
            return False

        value = False
        if not do_reuse:
            if self._checkpoint_at_end:
                value = True
                self._last_triggers.append('at_end')
        elif f_init_max_timestamp is None:
            # No F_INIT messages received: reuse triggered on muscle_settings_in
            # message.
            _logger.debug('Reuse triggered by muscle_settings_in.'
                          ' Not creating a snapshot.')
        else:
            value = self.__should_save(f_init_max_timestamp)

        return value

    def update_checkpoints(self, timestamp: float) -> None:
        """Update last and next checkpoint times when a snapshot is made.

        Args:
            timestamp: timestamp as reported by the instance (or from incoming
                F_INIT messages for save_final_snapshot).
        """
        self._prevwall = self.elapsed_walltime()
        self._nextwall = self._wall.next_checkpoint(self._prevwall)

        self._prevsim = timestamp
        self._nextsim = self._sim.next_checkpoint(timestamp)

    def get_triggers(self) -> List[str]:
        """Get trigger description(s) for the current reason for checkpointing.
        """
        triggers = self._last_triggers
        self._last_triggers = []
        return triggers

    def __should_save(self, simulation_time: float) -> bool:
        """Check if a checkpoint should be taken

        Args:
            simulation_time: current/next timestamp as reported by the instance
        """
        if self._nextsim is None and self._prevsim is None:
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

        walltime = self.elapsed_walltime()
        self._cpts_considered_until = walltime

        self._last_triggers = []
        if self._nextwall is not None and walltime >= self._nextwall:
            self._last_triggers.append(f"wallclock_time >= {self._nextwall}")
        if self._nextsim is not None and simulation_time >= self._nextsim:
            self._last_triggers.append(f"simulation_time >= {self._nextsim}")
        return bool(self._last_triggers)
