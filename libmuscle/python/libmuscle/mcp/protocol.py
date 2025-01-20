from enum import Enum


class RequestType(Enum):
    """Identifier for different types of request

    The MUSCLE Communication Protocol (MCP) defines a simple Remote Procedure
    Call protocol in which a request is sent to the server and a response is
    sent back to the calling client. In MCP, both of these are chunks of bytes.

    The MUSCLE Manager Protocol, MUSCLE Peer Protocol and MUSCLE Agent Protocol
    define the encoded messages sent in those chunks, using MsgPack encoding.
    To distinguish different kinds of requests, a request type identifier is
    used, as represented by this class.
    """
    # MUSCLE Manager Protocol
    REGISTER_INSTANCE = 1
    GET_PEERS = 2
    DEREGISTER_INSTANCE = 3
    GET_SETTINGS = 4
    SUBMIT_LOG_MESSAGE = 5
    SUBMIT_PROFILE_EVENTS = 6
    SUBMIT_SNAPSHOT = 7
    GET_CHECKPOINT_INFO = 8
    # Connection deadlock detection
    WAITING_FOR_RECEIVE = 9
    WAITING_FOR_RECEIVE_DONE = 10
    IS_DEADLOCKED = 11

    # MUSCLE Peer Protocol
    GET_NEXT_MESSAGE = 21

    # MUSCLE Agent Protocol
    REPORT_RESOURCES = 41
    GET_COMMAND = 42
    REPORT_RESULT = 43


class ResponseType(Enum):
    """Identifier for different types of response

    MCP Responses may be of different kinds, as described by this class.
    These are currently only used by the MUSCLE Manager Protocol.
    """
    # MUSCLE Manager Protocol
    SUCCESS = 0
    ERROR = 1
    PENDING = 2


class AgentCommandType(Enum):
    """Identifier for different types of commands

    These are requested from the manager by the agent, and tell it what to do. Part
    of the MUSCLE Agent Protocol, used in the response to RequestType.GET_COMMAND.
    """
    START = 1
    CANCEL_ALL = 2
    SHUTDOWN = 3
