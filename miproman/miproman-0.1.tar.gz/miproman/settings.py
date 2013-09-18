import os

from miproman.argument_parser import _parse_args
from miproman.config_parser import _parse_config

DEFAULT_PROFILE_PATH = os.path.join(
    os.environ["HOME"],
    "Library",
    "Preferences",
    "com.googlecode.iterm2.plist"
)

DEFAULTS = {
    "servers": None,
    "command": "ssh {0}",
    "tags": [],
    "range": [1,2],
    "profile": DEFAULT_PROFILE_PATH,
    "template_name": "Default",
    "verbose": False,
}

def _has_value(items):
    return items[1]

def get_settings():
    options = filter(_has_value, _parse_args())
    user_settings = filter(_has_value, _parse_config())

    settings = dict()
    settings.update(DEFAULTS)
    settings.update(user_settings)
    settings.update(options)
    settings["profile"] = settings["profile"].replace("~", os.environ["HOME"])

    return settings
