from threading import Condition
from typing import Dict  # noqa
from typing import List

from ymmsl import Port, Reference


class AlreadyRegistered(RuntimeError):
    pass


class InstanceRegistry:
    """Keeps track of running instances.

    The InstanceRegistry is a simple in-memory database that stores
    information about running instances of simulation components.
    """
    def __init__(self) -> None:
        """Construct an empty InstanceRegistry"""
        self._deregistered_one = Condition()    # doubles as lock
        self._locations = dict()  # type: Dict[Reference, List[str]]
        self._ports = dict()  # type: Dict[Reference, List[Port]]
        self._startup = True

    def add(self, name: Reference, locations: List[str], ports: List[Port]
            ) -> None:
        """Add an instance to the registry.

        Args:
            name: Name of the instance.
            locations: Network locations where it can be reached.
            ports: List of ports of this instance.

        Raises:
            ValueError: If an instance with this name has already been
                    registered.
        """
        with self._deregistered_one:
            if name in self._locations:
                raise AlreadyRegistered(
                        'Instance {} tried to register twice'.format(name))

            self._locations[name] = locations
            self._ports[name] = ports
            self._startup = False

    def get_locations(self, name: Reference) -> List[str]:
        """Retrieves the locations of a registered instance.

        Args:
            name: The name of the instance to get the location of.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        with self._deregistered_one:
            return self._locations[name]

    def get_ports(self, name: Reference) -> List[Port]:
        """Retrieves the ports of a registered instance.

        Args:
            name: The name of the instance whose ports to retrieve.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        with self._deregistered_one:
            return self._ports[name]

    def remove(self, name: Reference) -> None:
        """Remove an instance from the registry.

        Args:
            name: Name of the instance to remove.

        Raises:
            KeyError: If the instance does not exist.
        """
        with self._deregistered_one:
            del self._locations[name]
            del self._ports[name]
            self._deregistered_one.notify()

    def wait(self) -> None:
        """Waits until all instances are deregistered.

        This function blocks, and returns after each instance has been
        registered and deregistered again, signally the end of the
        simulation run.
        """
        # This is called from a different thread than add/remove
        with self._deregistered_one:
            while self._startup or self._locations:
                self._deregistered_one.wait()
