from typing import List

from libmuscle.mmp_client import MMPClient
from libmuscle.profiling import ProfileEvent, ProfileTimestamp


class Profiler:
    """Collects profiling events and sends them to the manager.
    """
    def __init__(self, manager: MMPClient) -> None:
        """Create a Profiler.

        Args:
            manager: The client used to submit data to the manager.
        """
        # TODO: use a background thread for flushing
        self._manager = manager
        self._events = list()   # type: List[ProfileEvent]

    def shutdown(self) -> None:
        self.__flush()

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
        self._events.append(event)
        if len(self._events) >= 100:
            self.__flush()

    def __flush(self) -> None:
        if self._events:
            self._manager.submit_profile_events(self._events)
            self._events.clear()
