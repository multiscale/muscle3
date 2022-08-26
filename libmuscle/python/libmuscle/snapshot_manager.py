import bisect
from typing import List, Optional, Union

from ymmsl import CheckpointRange, CheckpointRules


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

    def __init__(self, checkpoint_rules: CheckpointRules) -> None:
        """Create a new combined checkpoint trigger from the given rules

        Args:
            checkpoint_rules: checkpoint rules (from ymmsl) defining "every",
                "at", and/or "ranges" rules
        """
        self._triggers = []  # type: List[CheckpointTrigger]
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
