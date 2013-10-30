"""
***********
configs.api
***********

This module implements the configs API.
"""

from .config import Config

def load(config_file, fallback_file=None, defaults={}):
    """Constructs and returns a :class:`Config <Config>` instance.

    :param config_file: configuration file to be parsed
    :param fallback_file: (optional) fallback configuration file with default values to be used if missing in the ``config_file``
    :param: defaults: (optional) dict of default values to be used if missing in both ``config_file`` and ``fallback_file``

    Usage::

        >>> import configs

        >>> fc = configs.load('sample.conf', fallback_file='default.conf')

        >>> fc['general']['spam']
        eggs
    """

    return Config(config_file, fallback_file, defaults)
