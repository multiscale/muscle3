from typing import cast, Dict, List

from ymmsl import Endpoint, Reference, Operator

from libmuscle.operator import operator_from_grpc

import muscle_manager_protocol.muscle_manager_protocol_pb2 as mmp


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
        self.__endpoints = dict()  # type: Dict[str, Endpoint]

    def add(self, name: Reference, location: str, endpoints: List[Endpoint]
            ) -> None:
        """Add an instance to the registry.

        Args:
            name: Name of the instance.
            location: Network location where it can be reached.
            endpoints: List of endpoints of this instance.

        Raises:
            ValueError: If an instance with this name has already been
                    registered.
        """
        sname = str(name)
        if sname in self.__locations or sname in self.__endpoints:
            raise ValueError('Instance already registered')
        self.__locations[sname] = location
        self.__endpoints[sname] = endpoints

    def get_location(self, name: Reference) -> str:
        """Retrieves the location of a registered instance.

        Args:
            name: The name of the instance to get the location of.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        return self.__locations[str(name)]

    def get_endpoints(self, name: Reference) -> List[Endpoint]:
        """Retrieves the endpoints of a registered instance.

        Args:
            name: The name of the instance whose endpoints to retrieve.

        Raises:
            KeyError: If no instance with this name was registered.
        """
        # cast should be removable once we fix mypy ymmsl import
        return cast(List[Endpoint], self.__endpoints[str(name)])

    def remove(self, name: Reference) -> None:
        """Remove an instance from the registry.

        Args:
            name: Name of the instance to remove.

        Raises:
            KeyError: If the instance does not exist.
        """
        del(self.__locations[str(name)])
        del(self.__endpoints[str(name)])
