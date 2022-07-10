from enum import Enum
import time
from typing import Optional

from ymmsl import Port, Reference

from libmuscle.timestamp import Timestamp


class ProfileEventType(Enum):
    """Profiling event types for MUSCLE3.

    These match the types in the MUSCLE Manager Protocol, and should \
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

    Args:
        instance_id: The identifier of the instance that generated \
                this message.
        start_time: When the event started (real-world, not \
                simulation time).
        stop_time: When the event ended (real-world, not simulation \
                time).
        event_type: Type of event that was measured.
        port: Port used for sending or receiving, if applicable.
        port_length: Length of that port, if a vector.
        slot: Slot that was sent or received on, if applicable.
        message_size: Size of the message involved, if applicable.

    Attributes:
        instance_id: The identifier of the instance that generated \
                this message.
        start_time: When the event started (real-world, not \
                simulation time).
        stop_time: When the event ended (real-world, not simulation \
                time).
        event_type: Type of event that was measured.
        port: Port used for sending or receiving, if applicable.
        port_length: Length of that port, if a vector.
        slot: Slot that was sent or received on, if applicable.
        message_size: Size of the message involved, if applicable.
    """
    def __init__(
            self,
            instance_id: Reference,
            start_time: Timestamp,
            stop_time: Timestamp,
            event_type: ProfileEventType,
            port: Optional[Port] = None,
            port_length: Optional[int] = None,
            slot: Optional[int] = None,
            message_size: Optional[int] = None
            ) -> None:

        self.instance_id = instance_id
        self.start_time = start_time
        self.stop_time = stop_time
        self.event_type = event_type
        self.port = port
        self.port_length = port_length
        self.slot = slot
        self.message_size = message_size

    def stop(self) -> None:
        """Sets stop_time to the current time.
        """
        self.stop_time = Timestamp(time.time())
