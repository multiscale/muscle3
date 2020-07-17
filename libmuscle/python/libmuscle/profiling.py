from enum import Enum
import time
from typing import Dict, Optional

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp
from ymmsl import Port, Reference

from libmuscle.port import optional_port_to_grpc
from libmuscle.timestamp import Timestamp


class ProfileEventType(Enum):
    """Profiling event types for MUSCLE 3.

    These match the types in the MUSCLE Manager Protocol, and should \
    be kept identical to those.
    """
    REGISTER = 0
    CONNECT = 4
    DEREGISTER = 1
    SEND = 2
    RECEIVE = 3

    @staticmethod
    def from_grpc(
            event_type: mmp.ProfileEventType
            ) -> 'ProfileEventType':
        """Creates an event type from a gRPC-generated message.

        Args:
            event_type: A profile event type, received from gRPC.

        Returns:
            The same event type, as a ProfileEventType.
        """
        event_type_map = {
                mmp.PROFILE_EVENT_TYPE_REGISTER: ProfileEventType.REGISTER,
                mmp.PROFILE_EVENT_TYPE_CONNECT: ProfileEventType.CONNECT,
                mmp.PROFILE_EVENT_TYPE_DEREGISTER: ProfileEventType.DEREGISTER,
                mmp.PROFILE_EVENT_TYPE_SEND: ProfileEventType.SEND,
                mmp.PROFILE_EVENT_TYPE_RECEIVE: ProfileEventType.RECEIVE
                }  # type: Dict[mmp.ProfileEventType, ProfileEventType]
        return event_type_map[event_type]

    def to_grpc(self) -> mmp.ProfileEventType:
        """Converts the event type to the gRPC generated type.

        Returns:
            The current event type, as the gRPC type.
        """
        event_type_map = {
                ProfileEventType.REGISTER: mmp.PROFILE_EVENT_TYPE_REGISTER,
                ProfileEventType.CONNECT: mmp.PROFILE_EVENT_TYPE_CONNECT,
                ProfileEventType.DEREGISTER: mmp.PROFILE_EVENT_TYPE_DEREGISTER,
                ProfileEventType.SEND: mmp.PROFILE_EVENT_TYPE_SEND,
                ProfileEventType.RECEIVE: mmp.PROFILE_EVENT_TYPE_RECEIVE,
                }  # type: Dict[ProfileEventType, mmp.ProfileEventType]
        return event_type_map[self]


class ProfileEvent:
    """A profile event as used by MUSCLE 3.

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

    def to_grpc(self) -> mmp.ProfileEvent:
        """Converts the profile event to the gRPC-generated type.

        Returns:
            This profile event, as the gRPC type.
        """
        return mmp.ProfileEvent(
                instance_id=str(self.instance_id),
                start_time=self.start_time.to_grpc(),
                stop_time=self.stop_time.to_grpc(),
                event_type=self.event_type.to_grpc(),
                port=optional_port_to_grpc(self.port),
                port_length=self.port_length,
                slot=self.slot,
                message_size=self.message_size)
