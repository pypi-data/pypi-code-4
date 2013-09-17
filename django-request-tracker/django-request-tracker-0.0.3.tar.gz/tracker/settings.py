from django.conf import settings
from django.utils import importlib
from django.utils import six

USER_SETTINGS = getattr(settings, 'TRACKER_SETTINGS', None)


DEFAULTS = {
    'DEFAULT_BACKENDS': (
        'tracker.backends.GoogleAnalytics',
    ),
}

IMPORT_STRINGS = (
    'DEFAULT_BACKENDS',
)

def perform_import(val, setting_name):
    if isinstance(val, six.string_types):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val

def import_from_string(val, setting_name):
    try:
        parts = val.split('.')
        module_path, class_name = '.'.join(parts[:-1]), parts[-1]
        module = importlib.import_module(module_path)
        return getattr(module, class_name)
    except ImportError as e:
        msg = "Could not import '%s' for tracker setting '%s'. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)

class TrackerSettings(object):
    def __init__(self, user_settings=None, defaults=None, import_strings=None):
        self.user_settings = user_settings or {}
        self.defaults = defaults or {}
        self.import_strings = import_strings or ()

    def __getattr__(self, attr):
        if attr not in self.defaults.keys():
            raise AttributeError("Invalid Tracker setting: '%s'" % attr)

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Fall back to defaults
            val = self.defaults[attr]

        # Coerce import strings into classes
        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # Cache the result
        setattr(self, attr, val)
        return val

    def validate_setting(self, attr, val):
        pass

tracker_settings = TrackerSettings(USER_SETTINGS, DEFAULTS, IMPORT_STRINGS)
