from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import msgpack

from libmuscle.mcp.protocol import AgentCommandType, RequestType, ResponseType
from libmuscle.mcp.tcp_transport_client import TcpTransportClient
from libmuscle.native_instantiator.agent.agent_commands import (
        AgentCommand, StartCommand, CancelAllCommand, ShutdownCommand)


class MAPClient:
    """The client for the MUSCLE Agent Protocol.

    This class connects to the AgentManager and communicates with it.
    """
    def __init__(self, node_id: str, location: str) -> None:
        """Create a MAPClient

        Args:
            node_id: Id of the local node
            location: A connection string of the form hostname:port
        """
        self._node_id = node_id
        self._transport_client = TcpTransportClient(location)

    def close(self) -> None:
        """Close the connection

        This closes the connection. After this no other member functions can be called.
        """
        self._transport_client.close()

    def report_resources(self, resources: Dict[str, Any]) -> None:
        """Report local resources

        The only key in the dict is currently 'cpu', and it maps to a list of frozensets
        of hwthread ids that we can bind to with taskset or in a rankfile.

        Args:
            resources: Available resource ids by type
        """
        enc_cpu_resources = [
                list(hwthreads) for hwthreads in resources['cpu']]
        request = [
                RequestType.REPORT_RESOURCES.value,
                self._node_id, {'cpu': enc_cpu_resources}]
        self._call_agent_manager(request)

    def get_command(self) -> Optional[AgentCommand]:
        """Get a command from the agent manager.

        Returns:
            A command, or None if there are no commands pending.
        """
        request = [RequestType.GET_COMMAND.value, self._node_id]
        response = self._call_agent_manager(request)

        if response[0] == ResponseType.PENDING.value:
            return None
        else:
            command = msgpack.unpackb(response[1], raw=False)

        if command[0] == AgentCommandType.START.value:
            name = command[1]
            workdir = Path(command[2])
            args = command[3]
            env = command[4]
            stdout = Path(command[5])
            stderr = Path(command[6])

            return StartCommand(name, workdir, args, env, stdout, stderr)

        elif command[0] == AgentCommandType.CANCEL_ALL.value:
            return CancelAllCommand()

        elif command[0] == AgentCommandType.SHUTDOWN.value:
            return ShutdownCommand()

        raise Exception('Unknown AgentCommand')

    def report_result(self, names_exit_codes: List[Tuple[str, int]]) -> None:
        """Report results of finished processes.

        Args:
            names_exit_codes: A list of names and exit codes of finished processes.
        """
        request = [RequestType.REPORT_RESULT.value, names_exit_codes]
        self._call_agent_manager(request)

    def _call_agent_manager(self, request: Any) -> Any:
        """Call the manager and do en/decoding.

        Args:
            request: The request to encode and send

        Returns:
            The decoded response
        """
        encoded_request = msgpack.packb(request, use_bin_type=True)
        response, _ = self._transport_client.call(encoded_request)
        return msgpack.unpackb(response, raw=False)
