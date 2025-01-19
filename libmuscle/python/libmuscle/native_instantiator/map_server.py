import errno
import logging
from typing import Any, Dict, cast, List, Optional

import msgpack

from libmuscle.mcp.protocol import AgentCommandType, RequestType, ResponseType
from libmuscle.mcp.tcp_transport_server import TcpTransportServer
from libmuscle.mcp.transport_server import RequestHandler
from libmuscle.native_instantiator.agent.agent_commands import (
        AgentCommand, CancelAllCommand, ShutdownCommand, StartCommand)
from libmuscle.native_instantiator.iagent_manager import IAgentManager
from libmuscle.planner.resources import Core, CoreSet, OnNodeResources
from libmuscle.post_office import PostOffice

from ymmsl import Reference


_logger = logging.getLogger(__name__)


class MAPRequestHandler(RequestHandler):
    """Handles Agent requests."""
    def __init__(self, agent_manager: IAgentManager, post_office: PostOffice) -> None:
        """Create a MAPRequestHandler.

        Args:
            agent_manager: The AgentManager to forward reports to
            post_office: The PostOffice to get commands from
        """
        self._agent_manager = agent_manager
        self._post_office = post_office

    def handle_request(self, request: bytes) -> bytes:
        """Handles an agent request.

        Args:
            request: The encoded request

        Returns:
            response: An encoded response
        """
        req_list = msgpack.unpackb(request, raw=False)
        req_type = req_list[0]
        req_args = req_list[1:]
        if req_type == RequestType.REPORT_RESOURCES.value:
            response = self._report_resources(*req_args)
        elif req_type == RequestType.GET_COMMAND.value:
            response = self._get_command(*req_args)
        elif req_type == RequestType.REPORT_RESULT.value:
            response = self._report_result(*req_args)

        return cast(bytes, msgpack.packb(response, use_bin_type=True))

    def _report_resources(
            self, node_name: str, data: Dict[str, Any]) -> Any:
        """Handle a report resources request.

        This is used by the agent to report available resources on its node when
        it starts up.

        Args:
            node_name: Name (hostname) of the node
            data: Resource dictionary, containing a single key 'cpu' which maps to a
                list of cores, where each core is a list of ints, starting with the core
                id at index [0] followed by the hwthread ids of all hwthreads in this
                core.
        """
        cores = CoreSet((Core(ids[0], set(ids[1:])) for ids in data['cpu']))
        node_resources = OnNodeResources(node_name, cores)
        self._agent_manager.report_resources(node_resources)
        return [ResponseType.SUCCESS.value]

    def _get_command(self, node_name: str) -> Any:
        """Handle a get command request.

        This is used by the agent to ask if there's anything we would like it to do.
        Command sounds a bit brusque, but we already have the agent sending requests
        to this handler, so I needed a different word to distinguish them. Requests
        are sent by the agent to the manager (because it's the client in an RPC setup),
        commands are returned by the manager to the agent (because it tells it what to
        do).

        Args:
            node_name: Hostname (name) of the agent's node
        """
        node_ref = Reference('_' + node_name.replace('-', '_'))
        next_request: Optional[bytes] = None
        if self._post_office.have_message(node_ref):
            next_request = self._post_office.get_message(node_ref)

        if next_request is not None:
            return [ResponseType.SUCCESS.value, next_request]

        return [ResponseType.PENDING.value]

    def _report_result(self, instances: List[List[Any]]) -> Any:
        """Handle a report result rquest.

        This is sent by the agent if an instance it launched exited.

        Args:
            instances: List of instance descriptions, comprising an id str and exit
                    code int. Really a List[Tuple[str, int]] but msgpack doesn't know
                    about tuples.
        """
        self._agent_manager.report_result(list(map(tuple, instances)))
        return [ResponseType.SUCCESS.value]


class MAPServer:
    """The MUSCLE Agent Protocol server.

    This class accepts connections from the agents and services them using a
    MAPRequestHandler.
    """
    def __init__(self, agent_manager: IAgentManager) -> None:
        """Create a MAPServer.

        This starts a TCP Transport server and connects it to a MAPRequestHandler,
        which uses the given agent manager to service the requests. By default, we
        listen on port 9009, unless it's not available in which case we use a random
        other one.

        Args:
            agent_manager: AgentManager to forward requests to
        """
        self._post_office = PostOffice()
        self._handler = MAPRequestHandler(agent_manager, self._post_office)
        try:
            self._server = TcpTransportServer(self._handler, 9009)
        except OSError as e:
            if e.errno != errno.EADDRINUSE:
                raise
            self._server = TcpTransportServer(self._handler)

    def get_location(self) -> str:
        """Return this server's network location.

        This is a string of the form tcp:<hostname>:<port>.
        """
        return self._server.get_location()

    def stop(self) -> None:
        """Stop the server.

        This makes the server stop serving requests, and shuts down its
        background threads.
        """
        self._server.close()

    def deposit_command(self, node_name: str, command: AgentCommand) -> None:
        """Deposit a command for the given agent.

        This takes the given command and queues it for the given agent to pick up next
        time it asks us for one.

        Args:
            node_name: Name of the node whose agent should execute the command
            command: The command to send
        """
        agent = Reference('_' + node_name.replace('-', '_'))

        if isinstance(command, StartCommand):
            command_obj = [
                    AgentCommandType.START.value, command.name, str(command.work_dir),
                    command.args, command.env, str(command.stdout), str(command.stderr)
                    ]
        elif isinstance(command, CancelAllCommand):
            command_obj = [AgentCommandType.CANCEL_ALL.value]
        elif isinstance(command, ShutdownCommand):
            command_obj = [AgentCommandType.SHUTDOWN.value]

        encoded_command = cast(bytes, msgpack.packb(command_obj, use_bin_type=True))

        self._post_office.deposit(agent, encoded_command)
