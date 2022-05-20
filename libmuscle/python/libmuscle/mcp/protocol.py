from enum import Enum


class RequestType(Enum):
    REGISTER_INSTANCE = 1
    GET_PEERS = 2
    DEREGISTER_INSTANCE = 3
    GET_SETTINGS = 4
    GET_NEXT_MESSAGE = 6
    SUBMIT_LOG_MESSAGE = 7
    SUBMIT_PROFILE_EVENTS = 8


class ResponseType(Enum):
    SUCCESS = 0
    ERROR = 1
    PENDING = 2
