from enum import auto, Enum
from typing import Optional


class APIPhase(Enum):
    """Different phases that the user code traverses.

    These values describe different regions that the model code can be
    in for the case where checkpointing is implemented. By tracking
    the phase that the model should be in, we can detect incorrect API
    usage.

    This does not match the yMMSL operators, as it is more
    fine-grained and concerns checkpointing, which is not represented
    in the SEL.

    Note that AFTER_REUSE_INSTANCE and BEFORE_RESUMING refer to the
    same place in the code. AFTER_REUSE_INSTANCE is used when we
    don't know yet if the code has checkpointing support, and so we
    don't know whether the next call is to resuming() or to
    reuse_instance(). Once a checkpointing function has been called,
    we know that we should expect resume() after reuse_instance() and
    we use BEFORE_RESUMING accordingly.
    """
    BEFORE_REUSE_INSTANCE = auto()
    """Before calling reuse_instance"""

    AFTER_REUSE_INSTANCE = auto()
    """At the top of the reuse loop"""

    BEFORE_RESUMING = auto()
    """Between reuse_instance and resuming"""

    BEFORE_LOAD_SNAPSHOT = auto()
    """Between resuming and load_snapshot"""

    BEFORE_SHOULD_INIT = auto()
    """After resuming, before should_init"""

    BEFORE_SHOULD_SAVE_SNAPSHOT = auto()
    """Between should_init and should_save*"""

    BEFORE_SAVE_SNAPSHOT = auto()
    """Between should_save_snapshot and save_snapshot"""

    BEFORE_SAVE_FINAL_SNAPSHOT = auto()
    """Between should_save_final_snapshot and save_final_snapshot"""

    AFTER_REUSE_LOOP = auto()
    """After the final call to reuse_instance()"""


class APIGuard:
    """Keeps track of and checks in which phase the model is.

    The verify_* functions are called when the corresponding function
    on Instance is called, to check that we're in the right phase. They
    raise a RuntimeError if there's a problem. The *_done functions are
    called to signal that the corresponding function finished
    successfully, and that we are moving on to the next phase.
    """
    def __init__(self) -> None:
        """Create an APIPhaseTracker.

        This starts the tracker in BEFORE_REUSE_INSTANCE.
        """
        self._phase = APIPhase.BEFORE_REUSE_INSTANCE
        self._uses_checkpointing = None     # type: Optional[bool]

    def uses_checkpointing(self) -> bool:
        """Return whether the code is using checkpointing.

        We can only determine that the code doesn't use checkpointing
        if there are no checkpointing calls between the first and
        second calls to reuse_instance. So this function should only
        be called after the second call to verify_reuse_instance, or
        it may raise if the code does not use checkpointing.

        Raises:
            RuntimeError: if we are at a point where we cannot know
                the answer yet.
        """
        if self._uses_checkpointing is not None:
            return self._uses_checkpointing
        raise RuntimeError(
                'The API was implemented incorrectly, please consult the'
                ' documentation.')

    def verify_reuse_instance(self) -> None:
        """Check reuse_instance()"""
        if self._phase == APIPhase.AFTER_REUSE_INSTANCE:
            self._uses_checkpointing = False
        elif self._phase != APIPhase.BEFORE_REUSE_INSTANCE:
            raise RuntimeError()

    def reuse_instance_done(self, reusing: bool) -> None:
        """Update phase on successful reuse_instance().

        Args:
            reusing: Whether we are reusing or not.
        """
        if not reusing:
            self._phase = APIPhase.AFTER_REUSE_LOOP
        else:
            if self._uses_checkpointing is None:
                self._phase = APIPhase.AFTER_REUSE_INSTANCE
            elif self._uses_checkpointing:
                self._phase = APIPhase.BEFORE_RESUMING
            else:
                self._phase = APIPhase.BEFORE_REUSE_INSTANCE

    def verify_resuming(self) -> None:
        """Check resuming()"""
        if self._phase not in (
                APIPhase.BEFORE_RESUMING, APIPhase.AFTER_REUSE_INSTANCE):
            raise RuntimeError(
                    'Please call resuming() only as the first thing in the'
                    ' reuse loop.')

    def resuming_done(self, resuming: bool) -> None:
        """Update phase on successful resuming().

        Args:
            resuming: Whether we're resuming or not.
        """
        self._uses_checkpointing = True
        if resuming:
            self._phase = APIPhase.BEFORE_LOAD_SNAPSHOT
        else:
            self._phase = APIPhase.BEFORE_SHOULD_INIT

    def verify_load_snapshot(self) -> None:
        """Check load_snapshot()"""
        if self._phase != APIPhase.BEFORE_LOAD_SNAPSHOT:
            raise RuntimeError(
                    'Please check that we are resuming by calling resuming()'
                    ' before calling load_snapshot()')

    def load_snapshot_done(self) -> None:
        """Update phase on successful load_snapshot()"""
        self._phase = APIPhase.BEFORE_SHOULD_INIT

    def verify_should_init(self) -> None:
        """Check should_init()"""
        if self._phase != APIPhase.BEFORE_SHOULD_INIT:
            raise RuntimeError(
                    'Please check whether to run f_init using should_init()'
                    ' after resuming, and before trying to save a snapshot.')

    def should_init_done(self) -> None:
        """Update phase on successful should_init()"""
        self._phase = APIPhase.BEFORE_SHOULD_SAVE_SNAPSHOT

    def verify_should_save_snapshot(self) -> None:
        """Check should_save_snapshot()"""
        if self._phase != APIPhase.BEFORE_SHOULD_SAVE_SNAPSHOT:
            raise RuntimeError(
                    'We reached the end of the reuse loop without checking'
                    ' if a snapshot should be saved. Please add at least'
                    ' a should_save_final_snapshot and save_final_snapshot.')

    def should_save_snapshot_done(self, should_save: bool) -> None:
        """Update phase on successful should_save_snapshot().

        Args:
            should_save: Whether we should save or not.
        """
        if should_save:
            self._phase = APIPhase.BEFORE_SAVE_SNAPSHOT

    def verify_save_snapshot(self) -> None:
        """Check should_save_snapshot()"""
        if self._phase != APIPhase.BEFORE_SAVE_SNAPSHOT:
            raise RuntimeError()

    def save_snapshot_done(self) -> None:
        """Update phase on successful save_snapshot()"""
        self._phase = APIPhase.BEFORE_SHOULD_SAVE_SNAPSHOT

    def verify_should_save_final_snapshot(self) -> None:
        """Check should_save_final_snapshot()."""
        if self._phase != APIPhase.BEFORE_SHOULD_SAVE_SNAPSHOT:
            if self._phase in (
                    APIPhase.BEFORE_REUSE_INSTANCE, APIPhase.AFTER_REUSE_LOOP):
                msg = (
                        'Please only call should_save_final_snapshot inside'
                        ' the reuse loop.')
            elif self._phase == APIPhase.BEFORE_SAVE_FINAL_SNAPSHOT:
                msg = (
                        'If should_save_final_snapshot returns True, then you'
                        ' must call save_final_snapshot immediately.')
            elif self._phase == APIPhase.BEFORE_SAVE_SNAPSHOT:
                msg = (
                        'If should_save_snapshot returns True, then you must'
                        ' call save_snapshot first.')
            else:
                msg = (
                        'Please only call should_save_final_snapshot at the'
                        ' end of the reuse loop.')

            raise RuntimeError(msg)

    def should_save_final_snapshot_done(self, should_save: bool) -> None:
        """Update phase on successful should_save_snapshot().

        Args:
            should_save: Whether we should save or not.
        """
        if should_save:
            self._phase = APIPhase.BEFORE_SAVE_FINAL_SNAPSHOT
        else:
            self._phase = APIPhase.BEFORE_REUSE_INSTANCE

    def verify_save_final_snapshot(self) -> None:
        """Check should_save_final_snapshot()"""
        if self._phase != APIPhase.BEFORE_SAVE_FINAL_SNAPSHOT:
            raise RuntimeError()

    def save_final_snapshot_done(self) -> None:
        """Updates state on successful save_final_snapshot()"""
        self._phase = APIPhase.BEFORE_REUSE_INSTANCE
