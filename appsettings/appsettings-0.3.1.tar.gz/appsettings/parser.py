import os
import argparse

import yaml

class SettingsParser(argparse.ArgumentParser):
    """
    An argparse.ArgumentParser subclass that also allows pulling values from
    environment variables or a YAML file.

    Command line options will always override any other method.

    Environment variables will override values from a YAML file.

    Only long options are handled (e.g. "--host").  Short options ("-h") and
    positional arguments are passed through to argparse unmolested.
    """

    def __init__(self, env=None, yaml_file=None, **kwargs):
        """
        'env', if provided, should be a dict.  Typically you'll pass in
        os.environ.

        'yaml_file', if provided, should be a file object that contains a
        yaml-formatted dict of config values.

        All other kwargs are passed through exactly to argparse.ArgumentParser.
        """

        # If no env provided, use os.environ
        self.env = env or os.environ

        # If no yaml_file provided, look for APP_SETTINGS_YAML
        self.yaml_file = yaml_file
        if not self.yaml_file and 'APP_SETTINGS_YAML' in self.env:
            self.yaml_file = open(os.environ['APP_SETTINGS_YAML'])

        if self.yaml_file:
            self.yaml_settings = yaml.safe_load(self.yaml_file)
        else:
            self.yaml_settings = {}

        self.env_settings = {}
        super(SettingsParser, self).__init__(**kwargs)

    def add_argument(self, name, *args, **kwargs):

        if name.startswith('--'):
            # For each option added, save the type and env var name in our dict
            # for lookups later.

            config_name = name[2:]

            evname = kwargs.pop('env_var', None)

            if evname:
                self.env_settings[config_name] = {
                    'type': kwargs.get('type', str),
                    'evname': evname,
                    'default': kwargs.get('default', None)
                } 

        return super(SettingsParser, self).add_argument(name, *args, **kwargs)

    def parse_args(self, *args, **kwargs):
        # the superclass's parse_args allows you to pass your own namespace
        # object, which it well then update.  We can take advantage of that by
        # creating one of our own, populating it with env/yaml values, then
        # feeding it to the superclass.
        namespace = argparse.Namespace()

        # Stick our parsed yaml settings on the namespace, if there were any.
        for setting in self.yaml_settings:
            setattr(namespace, setting, self.yaml_settings[setting])

        # Stick any env var settings on the namespace too.
        for setting in self.env_settings:
            converter, evname, val = self.env_settings[setting]
            if evname in os.environ:
                val = converter(os.environ[evname])
            setattr(namespace, setting, val)

        kwargs['namespace'] = namespace

        return super(SettingsParser, self).parse_args(*args, **kwargs)
