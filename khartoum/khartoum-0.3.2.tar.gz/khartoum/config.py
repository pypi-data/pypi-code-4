
# A dictionary of all config keys that the app cares about.  Each key should
# hold a tuple in the form (default_value, env var name, command line name).  A
# value of None for env var name or command line name means the key cannot be
# set by that method.
import argparse

class SettingsParser(argparse.ArgumentParser):
    """
    An argparse.ArgumentParser subclass that also allows pulling values from
    environment variables or a YAML file.
    """

    def __init__(self, yaml_file=None, **kwargs)


def get_config(argv, env):
    """
    """
        'host': '0.0.0.0',
        'port': 8000,
        'mongo_host': 'localhost',
        'mongo_port': None,
        'mongo_db': 'test',
        'mongo_collection': 'fs',
        # There's little point compressing pngs, jpgs, tar.gz files, etc, and it's
        # really slow, so save compression for the file types where it pays off.
