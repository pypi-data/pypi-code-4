import os
from ConfigParser import SafeConfigParser, NoSectionError

def _conf_path(root):
    return os.path.join(root, "miproman.conf")

CONFIG_LOCATIONS = [
    _conf_path(os.curdir),
    _conf_path(os.environ["HOME"]),
    _conf_path("/etc/miproman"),
    os.environ.get("MIPROMAN_CONF", "")
]

def _parse_config():
    config = SafeConfigParser()
    for _file in CONFIG_LOCATIONS:
        try:
            with open(_file) as source:
                config.readfp(source)
        except IOError:
            pass
    try:
        return config.items("settings")
    except NoSectionError:
        return []
