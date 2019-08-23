import threading
from typing import Any, cast, List, Tuple, Type

import msgpack
from ymmsl import Reference

from libmuscle.mcp.server import Server
from libmuscle.post_office import PostOffice


def handle_requests(context: Any, post_office: PostOffice) -> None:
    """Handles requests on a socket.
    """
    import pynng
    while True:
        try:
            receiver_id = context.recv().decode('utf-8')

            message = post_office.get_message(receiver_id)
            message_dict = {
                    'sender': str(message.sender),
                    'receiver': str(message.receiver),
                    'port_length': message.port_length,
                    'timestamp': message.timestamp,
                    'next_timestamp': message.next_timestamp,
                    'parameter_overlay': message.parameter_overlay,
                    'data': message.data}
            packed_message = msgpack.packb(message_dict, use_bin_type=True)

            context.send(packed_message)
        except pynng.exceptions.Closed:
            break


class TcpServer(Server):
    """A server that accepts MCP connections over NNG.
    """
    def __init__(self, instance_id: Reference, post_office: PostOffice
                 ) -> None:
        """Create a TcpServer.

        Args:
            instance_id: Id of the instance we're a server for.
            post_office: A PostOffice to obtain data from.
        """
        super().__init__(instance_id, post_office)

        import pynng
        self._socket = pynng.Rep0(listen='tcp://*:0')
        self._threads = list()  # type: List[threading.Thread]
        for i in range(3):
            handler_thread = threading.Thread(
                    target=handle_requests,
                    args=(self._socket.new_context(), post_office))
            handler_thread.start()
            self._threads.append(handler_thread)

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        return 'tcp:{}'.format(self._socket.listeners[0].local_address)

    def close(self) -> None:
        """Closes this server.

        Stops the server listening, waits for existing clients to
        disconnect, then frees any other resources.
        """
        self._socket.close()
        for handler_thread in self._threads:
            handler_thread.join()

    @property
    def post_office(self) -> PostOffice:
        """Export this so the server thread can use it.
        """
        return self._post_office
