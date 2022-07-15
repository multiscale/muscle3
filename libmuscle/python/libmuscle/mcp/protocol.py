from enum import Enum


class RequestType(Enum):
    """Identifier for different types of request

    The MUSCLE Communication Protocol (MCP) defines a simple Remote Procedure
    Call protocol in which a request is sent to the server and a response is
    sent back to the calling client. In MCP, both of these are chunks of bytes.

    The MUSCLE Manager Protocol and MUSCLE Peer Protocol define the encoded
    messages sent in those chunks, using MsgPack encoding. To distinguish
    different kinds of requests, a request type identifier is used, as
    represented by this class.
    """
    # MUSCLE Manager Protocol
    REGISTER_INSTANCE = 1
    GET_PEERS = 2
    DEREGISTER_INSTANCE = 3
    GET_SETTINGS = 4
    SUBMIT_LOG_MESSAGE = 5
    SUBMIT_PROFILE_EVENTS = 6

    # MUSCLE Peer Protocol
    GET_NEXT_MESSAGE = 21


class ResponseType(Enum):
    """Identifier for different types of response

    MCP Responses may be of different kinds, as described by this class.
    These are currently only used by the MUSCLE Manager Protocol.
    """
    # MUSCLE Manager Protocol
    SUCCESS = 0
    ERROR = 1
    PENDING = 2
