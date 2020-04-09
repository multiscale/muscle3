import numpy as np
import pytest

from libmuscle.grid import Grid


def test_grid() -> None:
    a = np.array([[1, 2, 3], [4, 5, 6]])
    grid = Grid(a)
    grid = Grid(a, ['x', 'y'])

    with pytest.raises(ValueError):
        grid = Grid(a, ['x'])

    with pytest.raises(ValueError):
        grid = Grid(a, ['x', 'y', 'z'])
