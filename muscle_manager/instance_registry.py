from typing import Dict  # noqa
from typing import cast, List

from ymmsl import Port, Reference


class InstanceRegistry:
    """Keeps track of running instances.

    The InstanceRegistry is a simple in-memory database that stores
    information about running instances of compute elements.
    """
    def __init__(self) -> None:
        """Construct an empty InstanceRegistry.
        """
        # We index on the string version of the Reference because they
        # are not immutable and hashable, so two References with the
        # same contents will not match.
        self.__locations = dict()  # type: Dict[str, str]
        self.__ports = dict()  # type: Dict[str, Port]

    def add(self, name: Reference, location: str, ports: List[Port]
            ) -> None:
        """Add an instance to the registry.

        Args:
            name: Name of the instance.
            location: Network location where it can be reached.
            ports: List of ports of this instance.

        Raises:
            ValueError: If an instance with this name has already been
                    registered.
        """
        sname = str(name)
        if sname in self.__locations or sname in self.__ports:
            raise ValueError('Instance already registered')
        self.__locations[sname] = location
        self.__ports[sname] = ports

    def get_location(self, name: Reference) -> str:
        """Retrieves the location of a registered instance.

        Args:
            name: The name of the instance to get the location of.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        return self.__locations[str(name)]

    def get_ports(self, name: Reference) -> List[Port]:
        """Retrieves the ports of a registered instance.

        Args:
            name: The name of the instance whose ports to retrieve.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        # cast should be removable once we fix mypy ymmsl import
        return cast(List[Port], self.__ports[str(name)])

    def remove(self, name: Reference) -> None:
        """Remove an instance from the registry.

        Args:
            name: Name of the instance to remove.

        Raises:
            KeyError: If the instance does not exist.
        """
        del(self.__locations[str(name)])
        del(self.__ports[str(name)])
