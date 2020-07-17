import numpy as np
import pytest

from libmuscle.grid import Grid


def test_grid() -> None:
    a = np.array([[1, 2, 3], [4, 5, 6]])
    _ = Grid(a)
    _ = Grid(a, ['x', 'y'])

    with pytest.raises(ValueError):
        _ = Grid(a, ['x'])

    with pytest.raises(ValueError):
        _ = Grid(a, ['x', 'y', 'z'])
