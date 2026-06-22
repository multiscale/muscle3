from libmuscle.port_manager import PortManager

class TimelineManager:
    """Tracks the current iteration position for each timeline in a multiscale
    simulation.

    The iteration is a list of integers, one per timeline/scale dimension, that
    identifies the current step within each nested loop of the simulation.
    """

    def __init__(self, port_manager: PortManager):
        self._iteration: list[int] = None
