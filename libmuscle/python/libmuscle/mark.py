from socket import SocketType


def before_tcp_receive(socket: SocketType) -> None:
    """Before receiving on the given TCP socket

    This gets monkeypatched to inject faults by the network connection fault tolerance
    integration tests.
    """
    pass


def before_tcp_send(socket: SocketType) -> None:
    """Before sending on the given TCP socket

    This gets monkeypatched to inject faults by the network connection fault tolerance
    integration tests.
    """
    pass
