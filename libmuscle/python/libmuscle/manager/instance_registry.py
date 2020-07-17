from enum import Enum
from threading import Condition
from typing import Dict  # noqa
from typing import List

from ymmsl import Port, Reference


class _InstanceStatus(Enum):
    EXPECTED = 0,
    REGISTERED = 1,
    DEREGISTERED = 2


class InstanceRegistry:
    """Keeps track of running instances.

    The InstanceRegistry is a simple in-memory database that stores
    information about running instances of compute elements.
    """
    def __init__(self, expected_instances: List[str]) -> None:
        """Construct an empty InstanceRegistry.

        Args:
            expected_instances: List of instance names expected to
                    register.
        """
        self.__status = dict()  # type: Dict[Reference, _InstanceStatus]
        self.__deregistered_one = Condition()   # doubles as lock for __status
        self.__locations = dict()  # type: Dict[Reference, List[str]]
        self.__ports = dict()  # type: Dict[Reference, List[Port]]

        for instance_name in expected_instances:
            self.__status[Reference(instance_name)] = _InstanceStatus.EXPECTED

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
        if name in self.__locations or name in self.__ports:
            raise ValueError('Instance already registered')
        with self.__deregistered_one:
            self.__status[name] = _InstanceStatus.REGISTERED
        self.__locations[name] = locations
        self.__ports[name] = ports

    def get_locations(self, name: Reference) -> List[str]:
        """Retrieves the locations of a registered instance.

        Args:
            name: The name of the instance to get the location of.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        return self.__locations[name]

    def get_ports(self, name: Reference) -> List[Port]:
        """Retrieves the ports of a registered instance.

        Args:
            name: The name of the instance whose ports to retrieve.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        return self.__ports[name]

    def remove(self, name: Reference) -> None:
        """Remove an instance from the registry.

        Args:
            name: Name of the instance to remove.

        Raises:
            KeyError: If the instance does not exist.
        """
        del(self.__locations[name])
        del(self.__ports[name])
        with self.__deregistered_one:
            self.__status[name] = _InstanceStatus.DEREGISTERED
            self.__deregistered_one.notify()

    def wait(self) -> None:
        """Waits until all instance are deregistered.

        This function blocks, and returns after each expected instance
        has been registered and deregistered again, signalling the end
        of the simulation run.
        """
        # this is called from a different thread than add/remove
        def all_deregistered() -> bool:
            return all(map(
                    lambda x: x == _InstanceStatus.DEREGISTERED,
                    self.__status.values()))

        with self.__deregistered_one:
            while not all_deregistered():
                self.__deregistered_one.wait()
