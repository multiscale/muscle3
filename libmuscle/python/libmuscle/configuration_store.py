from typing import Optional

from libmuscle.configuration import (Configuration, ParameterValue,
                                     has_parameter_type)

from ymmsl import Reference


class ConfigurationStore:
    """Stores the current configuration for a compute element instance.
    """
    def __init__(self) -> None:
        """Create a ConfigurationStore.

        Initialises the base layer to an empty Configuration.
        """
        self._base = Configuration()

    def set_base(self, base_config: Configuration) -> None:
        self._base = base_config

    def get_parameter(self, name: Reference,
                      typ: Optional[str] = None) -> ParameterValue:
        value = self._base[name]
        if typ is not None:
            if not has_parameter_type(value, typ):
                raise TypeError('Value for parameter {} is of type {},'
                                ' where a {} was expected.'.format(
                                    name, type(value), typ))
        return value
