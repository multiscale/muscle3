from typing import List, Optional, Set

from ymmsl import SettingValue, Reference, Settings


def has_setting_type(value: SettingValue, typ: str) -> bool:
    """Checks whether the value has the given type.

    Args:
        value: A setting value.
        typ: A setting type. Valid values are 'str', 'int', 'float',
                'bool', '[int]', '[float]', and '[[float]]'.

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
    elif typ == '[int]':
        if isinstance(value, list):
            if len(value) == 0 or isinstance(value[0], int):
                # We don't check everything here, the yMMSL loader does
                # a full type check, so we just need to discriminate.
                return True
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
    raise ValueError('Invalid setting type specified: {}'.format(typ))


class SettingsManager:
    """Manages the current settings for a component instance.
    """
    def __init__(self) -> None:
        """Create a SettingsManager.

        Initialises the base and overlay layers to an empty
        Settings object.

        A SettingsManager has two layers of settings, a base
        layer that contains an immutable collection of settings set in
        the simulation's yMMSL description, and an overlay layer that
        holds settings that have been set at run-time.

        Attributes:
            base: The base layer.
            overlay: The overlay layer.
        """
        self.base = Settings()
        self.overlay = Settings()

    def list_settings(self, instance_id: Reference) -> List[str]:
        """Returns the names of all the settings.

        This returns the names of all the settings, as the model would
        pass them to request settings. It returns

        - <setting_name> as-is
        - <instance_id>.<setting_name> as <setting_name>
        - <other_id>.<setting_name> not at all
        - <setting>.<setting> not at all

        Note that we don't return global settings with multipart names.
        Those are legal, but currently indistinguishable from settings
        intended for other components. We're not actually telling
        anyone that they're legal, so we can probably get away with
        that. If it becomes an issue, we'll have to get a list of
        instance ids from the manager so we can recognise them
        correctly.

        Args:
            instance_id: Our instance id.

        Return:
            A list of setting names.
        """
        def extract_names(settings: Settings) -> Set[str]:
            result: Set[str] = set()
            for name in settings:
                if len(name) == 1:
                    result.add(str(name))
                else:
                    id_len = len(instance_id)
                    if len(name) > id_len:
                        if name[:id_len] == instance_id:
                            result.add(str(name[id_len:]))
            return result

        names = extract_names(self.base)
        names.update(extract_names(self.overlay))
        return sorted(names)

    def get_setting(self, instance: Reference, setting_name: Reference,
                    typ: Optional[str] = None) -> SettingValue:
        """Returns the value of a setting.

        Args:
            instance: The instance that this value is for.
            setting_name: The name of the setting to get the value of.
            typ: An optional type designation; if specified the type
                    is checked for a match before returning. Valid
                    values are 'str', 'int', 'float', 'bool',
                    '[float]' and '[[float]]'.

        Raises:
            KeyError: If the setting has not been set.
            TypeError: If the setting was set to a value that does
                    not match `typ`.
            ValueError: If an invalid value was specified for `typ`
        """
        for i in range(len(instance), -1, -1):
            if i > 0:
                name = instance[:i] + setting_name
            else:
                name = setting_name

            if name in self.overlay:
                value = self.overlay[name]
                break
            elif name in self.base:
                value = self.base[name]
                break
        else:
            raise KeyError(('Value for setting "{}" was not set.'.format(
                setting_name)))

        if typ is not None:
            if not has_setting_type(value, typ):
                raise TypeError('Value for setting "{}" is of type {},'
                                ' where {} was expected.'.format(
                                    name, type(value), typ))
        return value
