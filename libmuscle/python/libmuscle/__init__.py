from libmuscle.communicator import Message
from libmuscle.grid import Grid
from libmuscle.instance import Instance, InstanceFlags
from libmuscle.manager.profile_database import ProfileDatabase
from libmuscle.version import __version__
from libmuscle import runner


# Note that libmuscle.version above is created by the build system; it's okay
# that it's not present.

__all__ = [
        '__version__', 'Grid', 'Instance', 'InstanceFlags', 'Message',
        'ProfileDatabase', 'runner']


# export InstanceFlag members to the module namespace
# adapted from https://github.com/python/cpython/blob/3.10/Lib/re.py#L179
globals().update(InstanceFlags.__members__)
__all__.extend(InstanceFlags.__members__)
