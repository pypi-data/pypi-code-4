"""
`settings`: Settings instance.

`get_setting` (`name`): Gets the setting from registry.

:example:
>>> get_setting('DEBUG')
False

`set_setting` (`name`, `value`): Sets the setting in registry.

:example:
>>> set_setting('DEBUG', True)
>>> get_setting('DEBUG')
True

`reset_to_defaults_settings`(): Resets the settings to default values.

:example:
>>> reset_to_defaults_settings()
>>> get_setting('DEBUG')
False
"""

__title__ = 'starbase.conf'
__author__ = 'Artur Barseghyan'
__all__ = ('get_setting', 'set_setting', 'settings', 'reset_to_defaults_settings',)

from starbase import defaults

class Settings(object):
    """
    Settings registry.
    """
    def __init__(self):
        self._settings = {}

    def set(self, name, value):
        """
        Override default settings.

        :param str name:
        :param mixed value:
        """
        self._settings[name] = value

    def get(self, name, default=None):
        """
        Gets a variable from local settings.

        :param str name:
        :param mixed default: Default value.
        :return mixed:
        """
        if name in self._settings:
            return self._settings.get(name, default)
        elif hasattr(defaults, name):
            return getattr(defaults, name, default)
        else:
            return default

    def reset_to_defaults(self):
        """
        Resets settings to defaults.
        """
        self._settings = {}


settings = Settings()

get_setting = settings.get

set_setting = settings.set

reset_to_defaults_settings = settings.reset_to_defaults
