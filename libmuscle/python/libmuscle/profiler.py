from random import uniform
from threading import Condition, Lock, Thread
import time
from typing import List

from libmuscle.mmp_client import MMPClient
from libmuscle.profiling import ProfileEvent, ProfileTimestamp


_COMMUNICATION_INTERVAL = 10.0  # seconds


class Profiler:
    """Collects profiling events and sends them to the manager.
    """
    def __init__(self, manager: MMPClient) -> None:
        """Create a Profiler.

        Args:
            manager: The client used to submit data to the manager.
        """
        # Protects all member variables and _flush()
        self._mutex = Lock()

        self._manager = manager
        self._enabled = True
        self._events: List[ProfileEvent] = []
        self._thread = Thread(target=self._communicate, daemon=True)
        self._done_cv = Condition(self._mutex)
        self._done = False
        self._next_send = 0.0

        self._thread.start()

    def shutdown(self) -> None:
        with self._mutex:
            if self._done:
                return

            self._done = True
            self._done_cv.notify_all()

        self._thread.join()

        # with the thread gone, there's no need to lock anymore
        self._flush()

    def set_level(self, level: str) -> None:
        """Set the detail level at which data is collected.

        Args:
            level: Either 'none' or 'all' to disable or enable sending
                    events to the manager.
        """
        with self._mutex:
            self._enabled = level == 'all'

    def record_event(self, event: ProfileEvent) -> None:
        """Record a profiling event.

        This will record the event, and may flush this and previously
        recorded events to the manager. If the time is still running,
        it will be stopped. Other than this the event must be complete
        when it is submitted. Do not use the event object after calling
        this function with it.

        Args:
            event: The event to record.
        """
        if event.stop_time is None:
            event.stop_time = ProfileTimestamp()

        if self._enabled:
            with self._mutex:
                self._events.append(event)
                if len(self._events) >= 10000:
                    self._flush()
                self._next_send = time.monotonic() + _COMMUNICATION_INTERVAL

    def _communicate(self) -> None:
        """Background thread that communicates with the manager.

        This runs in the background, and periodically sends events to
        the manager.
        """
        initial_delay = uniform(0.0, _COMMUNICATION_INTERVAL)

        with self._mutex:
            self._next_send = time.monotonic() + initial_delay

            while not self._done:
                now = time.monotonic()
                notified = self._done_cv.wait(self._next_send - now)
                if not notified:
                    now = time.monotonic()
                    if self._next_send <= now:
                        self._flush()
                        self._next_send = now + _COMMUNICATION_INTERVAL

    def _flush(self) -> None:
        """Send events to the manager and empty the queue.

        Make sure to lock self._mutex before calling this.
        """
        if self._events:
            self._manager.submit_profile_events(self._events)
            self._events.clear()
