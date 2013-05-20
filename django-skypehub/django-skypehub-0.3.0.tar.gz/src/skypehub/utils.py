# coding: utf-8

from Skype4Py.errors import SkypeError


SKYPE_HOOK_OPTIONS = {
    'Transport': 'x11',
}

_skype = None


def get_skype(force_create=False, **kwargs):
    """return skype object.
    """
    global _skype
    from Skype4Py import Skype
    options = get_skype_hook_options()
    options.update(kwargs)
    if _skype is None or force_create:
        _skype = Skype(**options)
    return _skype


def get_skype_hook_options():
    """return SKYPE_HOOK_OPTIONS
    """
    from django.conf import settings
    if hasattr(settings, 'SKYPE_HOOK_OPTIONS'):
        return settings.SKYPE_HOOK_OPTIONS
    if is_windows():
        return {}
    return SKYPE_HOOK_OPTIONS


def is_windows():
    """Detect Windows platform.
    """
    import platform
    return platform.system() == 'Windows'
