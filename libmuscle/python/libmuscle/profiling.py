from enum import Enum
from time import perf_counter_ns, time_ns
from typing import Optional

from ymmsl import Port


class ProfileEventType(Enum):
    """Profiling event types for MUSCLE3."""
    REGISTER = 0
    CONNECT = 4
    SEND = 2
    RECEIVE = 3
    RECEIVE_WAIT = 5
    RECEIVE_TRANSFER = 6
    RECEIVE_DECODE = 7
    SHUTDOWN_WAIT = 9
    DISCONNECT_WAIT = 8
    SHUTDOWN = 10
    DEREGISTER = 1


class ProfileTimestamp:
    """A timestamp for profiling.

    This has higher resolution than Timestamp, storing a number of
    nanoseconds since the UNIX epoch in an int.

    Attributes:
        nanoseconds: Nanoseconds since the UNIX epoch.
    """
    _time_ref = time_ns() - perf_counter_ns()

    def __init__(self, nanoseconds: Optional[int] = None) -> None:
        """Create a timestamp representing now.

        Args:
            nanoseconds: Time to set. If None, use the current time.
        """
        if nanoseconds is None:
            nanoseconds = perf_counter_ns() + self._time_ref
        self.nanoseconds = nanoseconds


class ProfileEvent:
    """A profile event as used by MUSCLE3.

    This represents a single measurement of the timing of some event
    that occurred while executing the simulation.

    Args:
        event_type: Type of event that was measured.
        start_time: When the event started (real-world, not
                simulation time).
        stop_time: When the event ended (real-world, not simulation
                time).
        port: Port used for sending or receiving, if applicable.
        port_length: Length of that port, if a vector.
        slot: Slot that was sent or received on, if applicable.
        message_number: Number of message on this port, if applicable.
                Starts at 0 for the first message sent or received.
        message_size: Size of the message involved, if applicable.
        message_timestamp: Timestamp sent with the message, if
                applicable.

    Attributes:
        event_type: Type of event that was measured.
        start_time: When the event started (real-world, not
                simulation time).
        stop_time: When the event ended (real-world, not simulation
                time).
        port: Port used for sending or receiving, if applicable.
        port_length: Length of that port, if a vector.
        slot: Slot that was sent or received on, if applicable.
        message_number: Number of message on this port, if applicable.
                Starts at 0 for the first message sent or received.
        message_size: Size of the message involved, if applicable.
        message_timestamp: Timestamp sent with the message, if
                applicable.
    """
    def __init__(
            self,
            event_type: ProfileEventType,
            start_time: Optional[ProfileTimestamp] = None,
            stop_time: Optional[ProfileTimestamp] = None,
            port: Optional[Port] = None,
            port_length: Optional[int] = None,
            slot: Optional[int] = None,
            message_number: Optional[int] = None,
            message_size: Optional[int] = None,
            message_timestamp: Optional[float] = None
            ) -> None:

        self.event_type = event_type
        self.start_time = start_time
        self.stop_time = stop_time
        self.port = port
        self.port_length = port_length
        self.slot = slot
        self.message_number = message_number
        self.message_size = message_size
        self.message_timestamp = message_timestamp

    def start(self) -> None:
        """Sets start_time to the current time.
        """
        self.start_time = ProfileTimestamp()

    def stop(self) -> None:
        """Sets stop_time to the current time.
        """
        self.stop_time = ProfileTimestamp()
