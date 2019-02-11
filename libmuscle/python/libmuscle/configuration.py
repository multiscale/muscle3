from collections import MutableMapping
from typing import Any, Dict, Iterator, List, Tuple, Union

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

    def __eq__(self, other: Any) -> bool:
        """Returns whether keys and values are identical.
        """
        if not isinstance(other, Configuration):
            return NotImplemented
        return self._store == other._store

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

    def copy(self) -> 'Configuration':
        """Makes a shallow copy of this configuration and returns it.
        """
        new_conf = Configuration()
        new_conf._store = self._store.copy()
        return new_conf


def has_parameter_type(value: ParameterValue, typ: str) -> bool:
    """Checks whether the value has the given type.

    Args:
        value: A parameter value.
        typ: A parameter type. Valid values are 'str', 'int', 'float',
                'bool', '[float]', and '[[float]]'.

    Returns:
        True if the type of value matches typ.

    Raises:
        ValueError: If the type specified is not valid.
    """
    par_type_to_type = {
            'str': str,
            'int': int,
            'float': float,
            'bool': bool
            }

    if typ in par_type_to_type:
        return isinstance(value, par_type_to_type[typ])
    elif typ == '[float]':
        if isinstance(value, list):
            if len(value) == 0 or isinstance(value[0], float):
                # We don't check everything here, the yMMSL loader does
                # a full type check, so we just need to discriminate.
                return True
        return False
    elif typ == '[[float]]':
        if isinstance(value, list):
            if len(value) == 0 or isinstance(value[0], list):
                # We don't check everything here, the yMMSL loader does
                # a full type check, so we just need to discriminate.
                return True
        return False
    raise ValueError('Invalid parameter type specified: {}'.format(typ))