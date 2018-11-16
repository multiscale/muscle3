from libmuscle.mmp_client import MMPClient

import sys
from typing import Optional


class Muscle3:
    """The main MUSCLE 3 API class.

    This class provides the main MUSCLE3 functionality needed to
    implement compute elements that work in MUSCLE.
    """
    def __init__(self) -> None:
        """Initialise MUSCLE3.

        Creating an object of type Muscle initialises MUSCLE3 and
        makes its functionality available.
        """
        self.__manager = None  # type: Optional[MMPClient]
        mmp_location = self.__extract_manager_location()
        if mmp_location is not None:
            self.__manager = MMPClient(mmp_location)

    def __extract_manager_location(self) -> Optional[str]:
        """Gets the manager network location from the command line.

        We use a --muscle-manager=<host:port> argument to tell the
        MUSCLE library how to connect to the manager. This function
        will extract this argument from the command line arguments,
        if it is present. Since we want to be able to run without
        a manager, it is optional.

        Returns:
            A connection string, or None.
        """
        # Neither getopt, optparse, or argparse will let me pick out
        # just one option from the command line and ignore the rest.
        # So we do it by hand.
        prefix = '--muscle-manager='
        for arg in sys.argv[1:]:
            if arg.startswith(prefix):
                return arg[len(prefix):]

        return None
