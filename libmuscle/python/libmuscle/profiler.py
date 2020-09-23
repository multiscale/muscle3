from time import time
from typing import List, Optional

from ymmsl import Port, Reference

from libmuscle.mmp_client import MMPClient
from libmuscle.profiling import ProfileEvent, ProfileEventType
from libmuscle.timestamp import Timestamp


class Profiler:
    """Collects profiling events and sends them to the manager.
    """
    def __init__(self, instance_id: Reference, manager: MMPClient) -> None:
        """Create a Profiler.

        Args:
            manager: The client used to submit data to the manager.
        """
        # TODO: use a background thread for flushing
        self._instance_id = instance_id
        self._manager = manager
        self._events = list()   # type: List[ProfileEvent]

    def start(self, event_type: ProfileEventType, port: Optional[Port] = None,
              port_length: Optional[int] = None, slot: Optional[int] = None,
              message_size: Optional[int] = None
              ) -> ProfileEvent:
        """Start measuring an event.

        Call this, then call stop() on the returned ProfileEvent at
        the end of the event.

        Args:
            instance_id: Instance for which this event occurred.
            event_type: Type of event that occurred.
            port: Port that was sent or received on.
            port_length: Length of the port, if vector.
            slot: Slot that was sent or received on.
            message_size: Size in bytes of the message.

        Returns:
            A new ProfileEvent.
        """
        if len(self._events) >= 100:
            self.__flush()

        now = Timestamp(time())
        event = ProfileEvent(self._instance_id, now, now, event_type, port,
                             port_length, slot, message_size)
        self._events.append(event)
        return event

    def shutdown(self) -> None:
        self.__flush()

    def record_event(self, event: ProfileEvent) -> None:
        """Record a profiling event.

        This will record the event, and may flush this and previously
        recorded events to the manager.

        Args:
            event: The event to record.
        """
        self._events.append(event)
        if len(self._events) >= 100:
            self.__flush()
        if event.event_type == ProfileEventType.DEREGISTER:
            self.__flush()

    def __flush(self) -> None:
        if self._events:
            self._manager.submit_profile_events(self._events)
            self._events.clear()
