import bisect
from datetime import datetime, timezone
import logging
import os
import time
from typing import List, Optional, Union

from ymmsl import CheckpointRange, CheckpointRules, Checkpoints


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

    def __init__(self, at: List[Union[float, int]]) -> None:
        """Create an "at" checkpoint trigger

        Args:
            at: list of checkpoint moments
        """
        self._at = at
        self._at.sort()  # ymmsl already sorts, but just to be sure

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

    def __init__(self, range: CheckpointRange) -> None:
        """Create a range of checkpoints

        Args:
            range: checkpoint range defining start, stop and step.
        """
        self._start = range.start
        self._stop = range.stop
        self._step = range.step
        self._last = None  # type: Union[int, float, None]
        if self._stop is not None:
            start = 0 if self._start is None else self._start
            diff = self._stop - start
            self._last = start + (diff // self._step) * self._step

    def next_checkpoint(self, cur_time: float) -> Optional[float]:
        if self._start is not None and cur_time < self._start:
            return float(self._start)
        if self._last is not None and cur_time >= self._last:
            return None
        start = 0 if self._start is None else self._start
        diff = cur_time - start
        return float(start + (diff // self._step + 1) * self._step)

    def previous_checkpoint(self, cur_time: float) -> Optional[float]:
        if self._start is not None and cur_time < self._start:
            return None
        if self._last is not None and cur_time > self._last:
            return float(self._last)
        start = 0 if self._start is None else self._start
        diff = cur_time - start
        return float(start + (diff // self._step) * self._step)


class CombinedCheckpointTriggers(CheckpointTrigger):
    """Checkpoint trigger based on a combination of "every", "at" and "ranges"
    """

    def __init__(self, checkpoint_rules: Optional[CheckpointRules]) -> None:
        """Create a new combined checkpoint trigger from the given rules

        Args:
            checkpoint_rules: checkpoint rules (from ymmsl) defining "every",
                "at", and/or "ranges" rules
        """
        self._triggers = []  # type: List[CheckpointTrigger]
        if checkpoint_rules is None:
            return
        if checkpoint_rules.every is not None:
            cp_range = CheckpointRange(step=checkpoint_rules.every)
            self._triggers.append(RangeCheckpointTrigger(cp_range))
        if checkpoint_rules.at:
            self._triggers.append(AtCheckpointTrigger(checkpoint_rules.at))
        for cp_range in checkpoint_rules.ranges:
            self._triggers.append(RangeCheckpointTrigger(cp_range))

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

    def __init__(self, reference_utctime: datetime, checkpoints: Checkpoints
                 ) -> None:
        self._monotonic_reference = _utc_to_monotonic(reference_utctime)

        self._wall = CombinedCheckpointTriggers(checkpoints.wallclocktime)
        self._prevwall = 0.0
        self._nextwall = self._wall.next_checkpoint(0.0)  # type: Optional[float]

        self._sim = CombinedCheckpointTriggers(checkpoints.simulationtime)
        self._prevsim = None        # type: Optional[float]
        self._nextsim = None        # type: Optional[float]
        self._sim_reset = True

        self._last_triggers = []    # type: List[str]
        self._first_reuse = True

        # These attributes are only used to check if implementations are
        # following the guidelines
        self._should_have_saved = False
        self._should_save_final_called = False
        self._saved_final_checkpoint = False

    def elapsed_walltime(self) -> float:
        """Returns elapsed wallclocktime in seconds.
        """
        return time.monotonic() - self._monotonic_reference

    def should_save_snapshot(self, timestamp: float,
                             next_timestamp: Optional[float]) -> bool:
        """Handles instance.should_save_snapshot
        """
        if self._should_have_saved:
            _checkpoint_error('"should_save_snapshot" or '
                              '"should_save_final_snapshot" returned positive'
                              ' but no snapshot was saved before the next call')

        value = False
        elapsed_walltime = self.elapsed_walltime()
        if next_timestamp is None:
            _logger.warning('No "next_timestamp" provided. Workflow may not'
                            ' be able to create a consistent snapshot. See '
                            'https://muscle3.readthedocs.io/en/latest/checkpoints.html')
            value = self.__should_save(elapsed_walltime, timestamp)
        else:
            value = self.__should_save(elapsed_walltime, next_timestamp)
        self._should_have_saved = value
        return value

    def should_save_final_snapshot(self, timestamp: float) -> bool:
        """Handles instance.should_save_final_snapshot
        """
        if self._should_have_saved:
            _checkpoint_error('"should_save_snapshot" or '
                              '"should_save_final_snapshot" returned positive'
                              ' but no snapshot was saved before the next call')

        value = False
        if self._max_f_init_next_timestamp is None:
            # If the messages on F_INIT do not supply a next_timestamp, we will
            # always snapshot just before O_I
            value = True
            self._last_triggers = ['No "next_timestamp" provided on F_INIT'
                                   ' messages']
        else:
            elapsed_walltime = self.elapsed_walltime()
            value = self.__should_save(elapsed_walltime,
                                       self._max_f_init_next_timestamp)

        self._should_have_saved = value
        self._should_save_final_called = True
        return value

    def reuse_instance(self, max_f_init_next_timestamp: Optional[float]
                       ) -> None:
        """Cleanup between instance reuse

        Args:
            max_f_init_next_timestamp: the maximum next_timestamp of all
                messages pre--received during F_INIT.
        """
        self._max_f_init_next_timestamp = max_f_init_next_timestamp

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

    def update_checkpoints(self, simulationtime: float, final: bool) -> float:
        """Update last and next checkpoint times when a snapshot is made

        Args:
            simulationtime: next timestamp as reported by the instance (if
                available, otherwise current timestamp)

        Returns:
            Current elapsed walltime
        """
        self._prevwall = self.elapsed_walltime()
        self._nextwall = self._wall.next_checkpoint(self._prevwall)

        if final and self._max_f_init_next_timestamp is not None:
            simulationtime = self._max_f_init_next_timestamp
        self._prevsim = simulationtime
        self._nextsim = self._sim.next_checkpoint(simulationtime)

        self._should_have_saved = False
        self._saved_final_checkpoint = final
        return self._prevwall

    def get_triggers(self) -> List[str]:
        """Get trigger description(s) for the current reason for checkpointing.
        """
        triggers = self._last_triggers
        self._last_triggers = []
        return triggers

    def __should_save(self, walltime: float, simulationtime: float) -> bool:
        """Check if a checkpoint should be taken

        Args:
            walltime: current wallclock time (elapsed since reference)
            simulationtime: current/next timestamp as reported by the instance
        """
        if self._sim_reset:
            # we cannot make assumptions about the start time of a simulation,
            # a t=-1000 could make sense if t represents years since CE
            # and we should not disallow checkpointing for negative t
            previous = self._sim.previous_checkpoint(simulationtime)
            if previous is not None:
                # there is a checkpoint rule before the current moment, assume
                # we should have taken a snapshot back then
                self._nextsim = previous
            else:
                self._nextsim = self._sim.next_checkpoint(simulationtime)
            self._sim_reset = False

        self._last_triggers = []
        if self._nextwall is not None and walltime >= self._nextwall:
            self._last_triggers.append(f"wallclocktime >= {self._nextwall}")
        if self._nextsim is not None and simulationtime >= self._nextsim:
            self._last_triggers.append(f"simulationtime >= {self._nextsim}")
        return bool(self._last_triggers)
