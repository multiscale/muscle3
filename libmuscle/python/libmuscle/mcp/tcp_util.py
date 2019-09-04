from socket import SocketType


class SocketClosed(Exception):
    """Raised when trying to read from a socket that was closed.
    """
    pass


def recv_all(socket: SocketType, length: int) -> bytes:
    """Receive length bytes from a socket.

    Args:
        socket: Socket to receive on.
        length: Number of bytes to receive.

    Raises:
        SocketClosed: If the socket was closed by the peer.
        RuntimeError: If a read error occurred.
    """
    databuf = bytearray(length)
    received_count = 0
    while received_count < length:
        bytes_left = length - received_count
        received_now = socket.recv_into(
            memoryview(databuf)[received_count:], bytes_left)

        if received_now == 0:
            raise SocketClosed("Socket closed while receiving")

        if received_now == -1:
            raise RuntimeError("Error receiving")

        received_count += received_now

    return databuf


def send_int64(socket: SocketType, data: int) -> None:
    """Sends an int as a 64-bit signed little endian number.

    Args:
        socket: The socket to send on.
        data: The number to send.

    Raises:
        RuntimeError: If there was an error sending the data.
    """
    buf = data.to_bytes(8, byteorder='little')
    socket.sendall(buf)


def recv_int64(socket: SocketType) -> int:
    """Receives an int as a 64-bit signed little endian number.

    Args:
        socket: The socket to receive on.

    Raises:
        SocketClosed: If the socket was closed by the peer.
        RuntimeError: If a read error occurred.
    """
    buf = recv_all(socket, 8)
    return int.from_bytes(buf, 'little')
