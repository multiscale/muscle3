import multiprocessing as mp
from multiprocessing.connection import Connection
import threading
from ymmsl import Reference

from libmuscle.post_office import PostOffice
import libmuscle.mcp.pipe_multiplexer as mux
from libmuscle.mcp.server import Server, ServerNotSupported


class PipeServer(Server):
    """A server that accepts MCP connections over pipes.

    This server uses the pipe_multiplexer module to service message
    requests arriving via a pipe to another process containing a
    compute element instance.
    """
    def __init__(self, instance_id: Reference, post_office: PostOffice
                 ) -> None:
        """Create a PipeServer.

        Args:
            instance_id: Id of the instance for which we're serving.
        """
        super().__init__(instance_id, post_office)
        if mux.can_communicate_for(instance_id):
            # close mux ends to allow clean shutdown
            mux.close_mux_ends(instance_id)

            self._mux_server_conn = mux.get_instance_server_conn(instance_id)
            self._shutdown_conn, self._handler_shutdown_conn = mp.Pipe()
            self._server_thread = threading.Thread(
                    target=self.__conn_request_handler,
                    name='PipeServer-{}'.format(instance_id), daemon=True)

            self._server_thread.start()
        else:
            raise ServerNotSupported(('Instance {} was not started via'
                                      ' Muscle3, cannot communicate via pipes'
                                      ' because the required set-up was not'
                                      ' done.').format(self._instance_id))

    def get_location(self) -> str:
        """Returns the location this server listens on.

        Returns:
            A string containing the location.
        """
        return mux.get_address_for(self._instance_id)

    def close(self) -> None:
        """Closes this server.

        Stops the server listening, waits for existing clients to
        disconnect, then frees any other resources.
        """
        self._shutdown_conn.close()
        self._server_thread.join()

    def __conn_request_handler(self) -> None:
        """Handles incoming connection requests from the mux.
        """
        conn_threads = list()
        while True:
            ready_conns = mp.connection.wait(
                    [self._mux_server_conn, self._handler_shutdown_conn])

            if self._mux_server_conn in ready_conns:
                try:
                    connection, client_id = self._mux_server_conn.recv()
                    conn_thread = threading.Thread(
                            target=self.__mcp_pipe_handler,
                            args=(client_id, connection),
                            name='PipeHandler-{}-{}'.format(
                                self._instance_id, client_id), daemon=True)
                    conn_thread.start()
                    conn_threads.append(conn_thread)
                except EOFError:
                    self._handler_shutdown_conn.close()
                    break

            if self._handler_shutdown_conn in ready_conns:
                self._handler_shutdown_conn.close()
                break

        self._mux_server_conn.close()

        # Wait for clients to disconnect
        for conn_thread in conn_threads:
            conn_thread.join()

    def __mcp_pipe_handler(self, client_id: Reference, connection: Connection
                           ) -> None:
        """Handles a single connection from a single client.

        Args:
            client_id: Id of the client we're talking to.
            connection: The connection with the client.
        """
        try:
            while True:
                receiver_id = connection.recv()
                msg = self._post_office.get_message(receiver_id)
                connection.send(msg)
        except EOFError:
            pass
