from enum import Enum
import logging
from os import sched_getaffinity

from libmuscle.native_instantiator import slurm


_logger = logging.getLogger(__name__)


class Scheduler(Enum):
    NONE = 0
    SLURM = 1


class ResourceDetector:
    """Detects available compute resources.

    This detects whether we're running locally or in a SLURM allocation, and returns
    available resources on request.
    """
    def __init__(self) -> None:
        """Create a ResourceDetector.

        Detects available resources and initialises the object, which can then be
        queried.
        """
        if slurm.in_slurm_allocation():
            _logger.info('Detected a SLURM allocation')
            self.scheduler = Scheduler.SLURM
            self.nodes = slurm.get_nodes()
            self.cores_per_node = slurm.get_cores_per_node()
            _logger.info(
                    f'We have {len(self.nodes)} nodes and a total of'
                    f' {sum(self.cores_per_node)} cores available')
        else:
            _logger.info('Running locally without a cluster scheduler')
            self.scheduler = Scheduler.NONE
            self.nodes = ['localhost']
            self.cores_per_node = [len(sched_getaffinity(0))]
            _logger.info(f'We have {sum(self.cores_per_node)} cores available')

    def on_cluster(self) -> bool:
        _logger.debug(f'On cluster: {self.scheduler}')
        return self.scheduler != Scheduler.NONE
