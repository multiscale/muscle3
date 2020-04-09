from typing import List, Optional

import numpy as np


class Grid:
    """Represents a grid of data to send or receive.

    Note that for received grids, the array of data is a read-only
    NumPy array. If you have another array that you want to put the
    received data into, use ``np.copyto(dest, source)`` to copy the
    contents of the received array across into your destination array.
    If you don't have an array yet and want a writable version of the
    received array, use ``array.copy()`` to create a writable copy.
    See the tutorial for examples.

    Attributes:
        array (np.ndarray): An array of data
        indexes (Optional[List[str]]): The names of the array's indexes.
    """
    def __init__(
            self, array: np.ndarray, indexes: Optional[List[str]] = None
            ) -> None:
        """Creates a Grid object.

        A Grid object represents an multi-dimensional array of data. It
        has a type, a shape, and optionally a list of index names.

        Supported data types are 4- and 8-byte integers (numpy.int32,
        numpy.int64), 4- and 8-byte floats (numpy.float32,
        numpy.float64), and booleans (np.bool_, np.bool8). The ``data``
        argument must be a NumPy array of one of those types.

        If ``indexes`` is given, then it must be a list of strings of
        the same length as the number of dimensions of ``data``, and
        contain the names of the indexes of the array. For a 2D
        Cartesian grid, these may be ``'x'`` and ``'y'`` for example,
        or for a polar grid, ``'phi'`` and ``'rho'``.

        Args:
            array: An array of data, of a supported type (see above).
            indexes: Names of the indexes (see above).
        """
        if indexes is not None:
            if len(indexes) != array.ndim:
                raise ValueError(
                        'Number of indexes must match number of array'
                        ' dimensions')

        self.array = array
        self.indexes = indexes
