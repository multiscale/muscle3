import os
import pathlib

from libmuscle.compute_element import ComputeElement


_here = pathlib.Path(__file__).resolve().parent
_version_file = _here / '..' / '..' / '..' / 'VERSION'
with _version_file.open('r') as f:
    __version__ = f.read().strip()

__all__ = ['__version__', 'ComputeElement']
