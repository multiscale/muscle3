from enum import Enum


class Operator(Enum):
    """An operator of a kernel.

    This is a combination of the Submodel Execution Loop operators,
    and operators for other components such as mappers.
    """
    NONE = 0
    F_INIT = 1
    O_I = 2
    S = 3
    B = 4
    O_F = 5
    MAP = 6
