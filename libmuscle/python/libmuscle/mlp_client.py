from typing import Any, Dict, List, Optional, Tuple
from time import sleep
from multiprocessing.pool import ApplyResult, ThreadPool

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

        self._pool = ThreadPool(1)
        self._async_usage_results: Optional[ApplyResult] = None

    def close(self) -> None:
        """Close the connection

        This closes the connection. After this no other member functions can be called.
        """
        self._transport_client.close()
        self._pool.close()

    def report_usage(self, instance_id_and_pids: List[Tuple[str, int]]) -> None:
        """Report usage of resources of processes with given (instance_id, pid)
        on this node.

        Args:
            instance_id_and_pids: List of (instance_id, pid) tuples
        """
        def get_usage(
                instance_id_and_pids: List[Tuple[str, int]]
                ) -> Dict[str, Tuple[float, int]]:
            """Function to be called async to determine cpu and memory usage
            of a process and its children, cpu usage is collected over a second and
            we don't want it to block the main thread
            """

            usage: Dict[str, Tuple[float, int]] = {}
            processes: Dict[str, List[psutil.Process]] = {}

            for instance_id_and_pid in instance_id_and_pids:
                try:
                    instance_id, pid = instance_id_and_pid
                    process = psutil.Process(pid)
                    # Get the process and its children
                    processes[instance_id] = [
                        child for child in process.children(recursive=True)
                    ] + [process]
                    # First call to cpu_percent(), to initialize the baseline I guess...
                    for process in processes[instance_id]:
                        process.cpu_percent()
                except psutil.Error:
                    continue
            sleep(1)
            for instance_id, proc_list in processes.items():
                try:
                    # Second call to cpu_percent(), to get the actual usage
                    cpu_usages = [process.cpu_percent() for process in proc_list]
                    cpu = sum(cpu_usages)
                    # Sum the memories of the processes and their children,
                    # not sure if this is the right choice...
                    mem_usages = [process.memory_info().vms for process in proc_list]
                    mem = sum(mem_usages)
                    usage[instance_id] = (cpu, mem)
                except psutil.Error:
                    continue

            return usage

        if len(instance_id_and_pids) == 0:
            """ Nothing to monitor, return """
            return

        usage: Dict[str, Tuple[float, int]] = {}

        if self._async_usage_results is not None:
            if self._async_usage_results.ready():
                usage = self._async_usage_results.get()
                self._async_usage_results = None
        else:
            self._async_usage_results = self._pool.apply_async(
                get_usage, (instance_id_and_pids,))

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
