from libmuscle.configuration import Configuration, ParameterValue

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

    def get_parameter(self, name: Reference) -> ParameterValue:
        return self._base[name]
