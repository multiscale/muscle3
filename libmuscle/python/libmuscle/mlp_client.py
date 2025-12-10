from typing import TYPE_CHECKING, Any, Dict, List, Tuple
from logging import Logger

import msgpack
import psutil
from libmuscle.mcp.protocol import RequestType
from libmuscle.mcp.tcp_transport_client import TcpTransportClient


class MLPClient:
    """The client for the MUSCLE Logging Protocol.

    This class connects to the Manager and communicates with it.
    """
    def __init__(self, node_name: str, location: str) -> None:
        """Create an MLPClient

        Args:
            node_name: Name (hostname) of the local node
            location: A connection string of the form hostname:port
        """
        self._node_name = node_name
        self._transport_client = TcpTransportClient(location)

    def close(self) -> None:
        """Close the connection

        This closes the connection. After this no other member functions can be called.
        """
        self._transport_client.close()

    def report_usage(self, pids: List[Tuple[str, int]], logger: Logger) -> None:
        """Report usage of resources of processes with given (instance_id, pid) on this node.

        Args:
            pids: List of (instance_id, pid) tuples
        """
        if len(pids) == 0:
            """ Nothing to monitor, return """
            return

        usage: Dict[str, Tuple[float, int]] = {}
        for instance_id, pid in pids:
            try:
                process = psutil.Process(pid)
                cpu = process.cpu_percent()
                mem = process.memory_info().vms
                logger.debug(f'PID {pid}: CPU {cpu}%, Memory {mem}')
                usage[instance_id] = (cpu, mem)
            except psutil.NoSuchProcess:
                logger.debug(f'PID {pid}: Process not found')

        if len(usage) < 1:
            """ Nothing to monitor """
            return

        request = [
                RequestType.REPORT_USAGE.value,
                self._node_name, usage]
        self._call_manager(request)

    def _call_manager(self, request: Any) -> Any:
        """Call the manager and do en/decoding.

        Args:
            request: The request to encode and send

        Returns:
            The decoded response
        """
        encoded_request = msgpack.packb(request, use_bin_type=True)
        response, _ = self._transport_client.call(encoded_request)
        return msgpack.unpackb(response, raw=False)
