import multiprocessing as mp
from multiprocessing.connection import Connection
# The below line seems to help avoid crashes, something to do with
# a background thread in the library and forking threaded processes.
from multiprocessing.resource_sharer import DupFd   # type: ignore
from typing import Dict, List, Tuple
import uuid

from ymmsl import Reference


# This doesn't really multiplex anything, it facilitates the creation
# of pipes between compute element instances running in different
# processes. It's kind of similar to the MUSCLE manager in that, but
# naming it manager would be even more confusing, so multiplexer it is.


class _InstancePipes:
    """Pipes for communicating between an instance and the mux.

    Objects of this class contain the endpoints for a set of two pipes
    that is used to communicate between the instance processes and the
    multiplexer. The multiplexer (in this module) facilitates the
    creation of peer-to-peer pipe connections between the processes.

    For each instance there is a server pipe, on which the instance
    listens for incoming connection requests, and a client pipe,
    through which an instance asks the multiplexer to create a
    connection to another instance.

    Attributes:
        server_mux_conn: Mux side of the server pipe.
        server_instance_conn: Instance side of the server pipe.
        client_mux_conn: Mux side of the client pipe
        client_instance_conn: Instance side of the client pipe.
    """
    def __init__(self) -> None:
        """Create an InstancePipes containing two new pipes.
        """
        self.server_mux_conn, self.server_instance_conn = mp.Pipe()
        self.client_mux_conn, self.client_instance_conn = mp.Pipe()

    def close_mux_ends(self) -> None:
        """Closes the mux ends of both the pipes.
        """
        self.server_mux_conn.close()
        self.client_mux_conn.close()

    def close_instance_ends(self) -> None:
        """Closes the instance ends of both the pipes.
        """
        self.server_instance_conn.close()
        self.client_instance_conn.close()


_instance_pipes = dict()     # type: Dict[Reference, _InstancePipes]


def add_instance(instance_id: Reference) -> None:
    """Adds pipes for an instance.

    Args:
        instance_id: Name of the new instance.
    """
    _instance_pipes[instance_id] = _InstancePipes()


def can_communicate_for(instance_id: Reference) -> bool:
    """Returns whether we can serve on pipes for this instance.

    If the instance was not started via Muscle3, then it will not be
    registered, and we cannot start a PipeServer for it. That's fine,
    but we need to know.

    Args:
        instance_id: Name of the requested instance.
    """
    return instance_id in _instance_pipes


def close_instance_ends(instance_id: Reference) -> None:
    """Closes the instance sides of the pipes for the given instance.

    Args:
        instance_id: The instance to close for.
    """
    _instance_pipes[instance_id].close_instance_ends()


def close_mux_ends(instance_id: Reference) -> None:
    """Closes the mux sides of the pipes for the given instance.

    Args:
        instance_id: The instance to close for.
    """
    _instance_pipes[instance_id].close_mux_ends()


def close_all_pipes() -> None:
    """Closes all the instance pipes.

    For example, because each instance process and the mux process have
    their own copies, so the main process doesn't need them and its
    copies should be closed.
    """
    instances = list()  # type: List[Reference]
    for instance_id in _instance_pipes.keys():
        close_instance_ends(instance_id)
        close_mux_ends(instance_id)
        instances.append(instance_id)

    for instance_id in instances:
        del(_instance_pipes[instance_id])


def get_instance_server_conn(instance_id: Reference) -> Connection:
    """Returns the instance side of the server pipe for this instance.

    Args:
        instance_id: The instance for which to get the pipe.

    Returns:
        The instance side of the server pipe.
    """
    return _instance_pipes[instance_id].server_instance_conn


def get_instance_client_conn(instance_id: Reference) -> Connection:
    """Returns the instance side of the client pipe for this instance.

    Args:
        instance_id: The instance for which to get the pipe.

    Returns:
        The instance side of the client pipe.
    """
    return _instance_pipes[instance_id].client_instance_conn


_process_uuid = uuid.uuid4()


def get_address_for(instance_id: Reference) -> str:
    """Returns the MUSCLE-address for the given instance.

    Args:
        instance_id: Id of the instance to get the address for.

    Returns:
        An address string that can be passed to the MUSCLE Manager.
    """
    return 'pipe:{}/{}'.format(_process_uuid, instance_id)


def can_connect_to(peer_address: str) -> bool:
    """Checks whether this multiplexer can make connections for the address.

    This does not check whether the peer is up and running and
    listening, just that it's in the right process tree.

    Args:
        peer_address: An address of the form <uuid>/<instance_id>.
    """
    if not peer_address.startswith('pipe:'):
        return False
    peer_uuid = peer_address[5:].split('/')[0]
    return peer_uuid == str(_process_uuid)


def run() -> None:
    """Runs the pipe-based communication multiplexer.

    This listens for connection requests from instances, and creates
    pipes between the requested instances so that they can exchange
    messages.

    Shuts down automatically when all client instances have shut down.
    """
    while len(_instance_pipes) > 0:
        client_pipes = {instance_id: pipes.client_mux_conn
                        for instance_id, pipes in _instance_pipes.items()}
        ready_pipes = mp.connection.wait(client_pipes.values())
        done_instances = list()
        for client_id, pipe in client_pipes.items():
            if pipe in ready_pipes:
                try:
                    requested_server = pipe.recv()
                    conn1, conn2 = mp.Pipe()
                    _instance_pipes[requested_server].server_mux_conn.send(
                            (conn1, client_id))
                    pipe.send(conn2)
                    # close our copy of this pipe, they'll do peer-to-peer
                    conn1.close()
                    conn2.close()
                except EOFError:
                    done_instances.append(client_id)
                    close_mux_ends(client_id)

        for done_instance in done_instances:
            del(_instance_pipes[done_instance])
