from enum import Enum
import logging
from socket import gethostname
from typing import List, Optional

import psutil

from libmuscle.native_instantiator.slurm import slurm


_logger = logging.getLogger(__name__)


class Scheduler(Enum):
    NONE = 0
    SLURM = 1


class GlobalResources:
    """Detects available compute resources.

    This detects whether we're running locally or in a SLURM allocation, and returns
    available resources on request. This class describes all the available resources,
    not the ones local to a node.

    Attributes:
        scheduler: The HPC scheduler we're running under, if any.
        nodes: List of hostnames of available nodes to run on.
        logical_cpus_per_node: Number of cores available on each node.
                List alongside nodes.
    """
    def __init__(self) -> None:
        """Create a GlobalResources.

        Detects available resources and initialises the object, which can then be
        queried.
        """
        if slurm().in_slurm_allocation():
            _logger.info('Detected a SLURM allocation')
            self.scheduler = Scheduler.SLURM
            self.nodes = slurm().get_nodes()
            self.logical_cpus_per_node = slurm().get_logical_cpus_per_node()
            _logger.info(
                    f'We have {len(self.nodes)} nodes and a total of'
                    f' {sum(self.logical_cpus_per_node)} logical CPUs available')
        else:
            _logger.info('Running locally without a cluster scheduler')
            self.scheduler = Scheduler.NONE
            self.nodes = [gethostname()]
            self.logical_cpus_per_node = [psutil.cpu_count(logical=True) or 0]
            _logger.info(
                    f'We have {self.logical_cpus_per_node[0]} logical CPUS available')

    def on_cluster(self) -> bool:
        """Return whether we're running on a cluster."""
        return self.scheduler != Scheduler.NONE

    def agent_launch_command(self, agent_cmd: List[str]) -> List[str]:
        """Return a command for launching one agent on each node.

        Args:
            agent_cmd: A command that will start the agent.
        """
        if self.scheduler == Scheduler.SLURM:
            return slurm().agent_launch_command(agent_cmd, len(self.nodes))
        return agent_cmd


_global_resources: Optional[GlobalResources] = None
"""Global resources object.

This is a singleton, and that's fine because it's created once and then read-only. Also,
it's used in two places, and making two objects logs everything twice which is annoying.
"""


def global_resources() -> GlobalResources:
    """Wrapper for _global_resources.

    This is here to ensure that the object gets created after we've configured logging,
    so that the log output it generates actually ends up in the manager log.

    The users are all in the main thread of the NativeInstantiator background process,
    so there's no need for a lock right now.
    """
    global _global_resources

    if _global_resources is None:
        _global_resources = GlobalResources()

    return _global_resources
