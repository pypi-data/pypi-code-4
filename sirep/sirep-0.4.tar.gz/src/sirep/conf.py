from django.conf import settings

from sirep import defaults

def get_setting(setting, override=None):
    """
    Get a setting from sirep conf module, falling back to the default. If override is not None, it will be used
    instead of the setting.

    :param str setting: Setting name.
    :param override: Default value (if not specified defaults to None).
    """
    if override is not None:
        return override
    if hasattr(settings, 'SIREP_%s' % setting):
        return getattr(settings, 'SIREP_%s' % setting)
    else:
        return getattr(defaults, setting)
