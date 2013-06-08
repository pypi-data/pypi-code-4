# coding=utf8

"""Configuration manager, config is in toml"""

from . import charset
from .exceptions import ConfigSyntaxError

import toml
from os.path import join
from os.path import exists


class Config(object):
    """Configuration manager"""

    filename = "config.toml"
    filepath = join(".", filename)
    # default configuration
    default = {
        'root_path': '',
        'blog': {
            'name': 'Blog\'s name',
            'description': 'Blog\'s description',
            'url': 'http://your-site.com',
            'theme': 'classic'
        },
        'author': {
            'name': 'me',
            'email': 'me@some.com'
        },
        'disqus': {
            'shortname': 'your-disqus_short-name'
        }
    }

    def read(self):
        """Read and parse config, return a dict"""

        if not exists(self.filepath):
            # if not exists, touch one
            open(self.filepath, "a").close()

        content = open(self.filepath).read().decode(charset)
        try:
            config = toml.loads(content)
        except toml.TomlSyntaxError:
            raise ConfigSyntaxError

        return config

config = Config()  # build a config instance
