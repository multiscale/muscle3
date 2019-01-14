from collections import MutableMapping
from typing import Dict, Iterator, List, Tuple, Union

from ymmsl import Experiment, Reference


ParameterValue = Union[str, int, float, List[float], List[List[float]]]


class Configuration(MutableMapping):
    """A store for model parameter settings.

    This class stores settings for a simulation.
    """
    def __init__(self) -> None:
        """Create an empty Configuration object.
        """
        self._store = dict()    # type: Dict[Reference, ParameterValue]

    def __getitem__(self, key: Union[str, Reference]) -> ParameterValue:
        """Returns an item, implements configuration[name]
        """
        if isinstance(key, str):
            key = Reference(key)
        return self._store[key]

    def __setitem__(self, key: Union[str, Reference], value: ParameterValue
                    ) -> None:
        """Sets a value, implements configuration[name] = value.
        """
        if isinstance(key, str):
            key = Reference(key)
        self._store[key] = value

    def __delitem__(self, key: Union[str, Reference]) -> None:
        """Deletes a value, implements del(configuration[name]).
        """
        if isinstance(key, str):
            key = Reference(key)
        del(self._store[key])

    def __iter__(self) -> Iterator[Tuple[Reference, ParameterValue]]:
        """Iterate through the configuration's key, value pairs.
        """
        return iter(self._store)  # type: ignore

    def __len__(self) -> int:
        """Returns the number of parameter settings.
        """
        return len(self._store)
