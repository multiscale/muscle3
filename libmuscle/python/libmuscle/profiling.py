from enum import Enum
from typing import Optional

from ymmsl import Port

from libmuscle.timestamp import Timestamp


class ProfileEventType(Enum):
    """Profiling event types for MUSCLE3.

    These match the types in the MUSCLE Manager Protocol, and should
    be kept identical to those.
    """
    REGISTER = 0
    CONNECT = 4
    DEREGISTER = 1
    SEND = 2
    RECEIVE = 3


class ProfileEvent:
    """A profile event as used by MUSCLE3.

    This represents a single measurement of the timing of some event
    that occurred while executing the simulation.

    Note that instance_id gets set by the profiler after submitting
    the event, so it doesn't get passed in the constructor.

    Args:
        event_type: Type of event that was measured.
        start_time: When the event started (real-world, not
                simulation time).
        stop_time: When the event ended (real-world, not simulation
                time).
        port: Port used for sending or receiving, if applicable.
        port_length: Length of that port, if a vector.
        slot: Slot that was sent or received on, if applicable.
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
        message_size: Size of the message involved, if applicable.
        message_timestamp: Timestamp sent with the message, if
                applicable.
    """
    def __init__(
            self,
            event_type: ProfileEventType,
            start_time: Optional[Timestamp] = None,
            stop_time: Optional[Timestamp] = None,
            port: Optional[Port] = None,
            port_length: Optional[int] = None,
            slot: Optional[int] = None,
            message_size: Optional[int] = None,
            message_timestamp: Optional[float] = None
            ) -> None:

        self.event_type = event_type
        self.start_time = start_time
        self.stop_time = stop_time
        self.port = port
        self.port_length = port_length
        self.slot = slot
        self.message_size = message_size
        self.message_timestamp = message_timestamp

    def start(self) -> None:
        """Sets start_time to the current time.
        """
        self.start_time = Timestamp()

    def stop(self) -> None:
        """Sets stop_time to the current time.
        """
        self.stop_time = Timestamp()
