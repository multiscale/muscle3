from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime, timedelta

import msgpack
import psutil
from libmuscle.mcp.protocol import RequestType
from libmuscle.mcp.tcp_transport_client import TcpTransportClient


class Usage:
    """Class to neatly contain the monitoring of the usage of instances on a node
    There are try-except blocks for psutil.Error, these usually get hit when a
    process/child no longer exists, this is not an error but the way of "life"
    ignore those errors and continue with the still existing processes
    """
    last_updated: Optional[datetime] = None
    processes: Dict[str, List[psutil.Process]] = {}

    def refresh_processes(self, instance_id_and_pids: List[Tuple[str, int]]) -> None:
        self.processes = {}
        for instance_id_and_pid in instance_id_and_pids:
            instance_id, pid = instance_id_and_pid
            try:
                process = psutil.Process(pid)
                # Get the process and its children
                self.processes[instance_id] = [
                    child for child in process.children(recursive=True)
                ] + [process]
                # First call to cpu_percent(), to initialize the baseline I guess...
                for process in self.processes[instance_id]:
                    try:
                        process.cpu_percent()
                    except psutil.Error:
                        continue
            except psutil.Error:
                continue
        self.last_updated = datetime.now()

    def record_usage(self) -> Dict[str, Tuple[float, int]]:
        usage: Dict[str, Tuple[float, int]] = {}
        for instance_id, proc_list in self.processes.items():
            # Second call to cpu_percent(), to get the actual usage
            cpu_usages = []
            mem_usages = []
            for process in proc_list:
                try:
                    cpu_usages.append(process.cpu_percent())
                    mem_usages.append(process.memory_info().vms)
                except psutil.Error:
                    continue

            cpu = sum(cpu_usages)
            # Sum the memories of the processes and their children,
            # not sure if this is the right choice...
            mem = sum(mem_usages)

            usage[instance_id] = (cpu, mem)
        self.last_updated = datetime.now()
        return usage


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
        self._usage = Usage()

    def close(self) -> None:
        """Close the connection

        This closes the connection. After this no other member functions can be called.
        """
        self._transport_client.close()

    def report_usage(self, instance_id_and_pids: List[Tuple[str, int]]) -> None:
        """Report usage of resources of processes with given (instance_id, pid)
        on this node.

        Args:
            instance_id_and_pids: List of (instance_id, pid) tuples
        """

        if len(instance_id_and_pids) == 0:
            """ Nothing to monitor, return """
            return

        refresh_processes = False
        record_usage = False

        if not self._usage.last_updated:
            refresh_processes = True
        elif self._usage.last_updated - timedelta(seconds=1) < datetime.now():
            record_usage = True
            refresh_processes = True

        usage: Dict[str, Tuple[float, int]] = {}
        if record_usage:
            usage = self._usage.record_usage()
        if refresh_processes:
            self._usage.refresh_processes(instance_id_and_pids)

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
