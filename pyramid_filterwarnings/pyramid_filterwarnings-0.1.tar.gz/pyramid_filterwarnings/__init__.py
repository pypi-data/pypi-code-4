# -*- coding: utf-8 -*-
import warnings
from pyramid.exceptions import ConfigurationError

__version__ = '0.1'


def get_category(settings, key):
    category = settings.get(key, 'Warning')
    warnings_cls = {'Warning': Warning,
                    'UserWarning': UserWarning,
                    'DeprecationWarning': DeprecationWarning,
                    'SyntaxWarning': SyntaxWarning,
                    'RuntimeWarning': RuntimeWarning,
                    'FutureWarning': FutureWarning,
                    'PendingDeprecationWarning': PendingDeprecationWarning,
                    'ImportWarning': ImportWarning,
                    'UnicodeWarning': UnicodeWarning,
                    }
    try:
        return warnings_cls[category]
    except KeyError:
        raise ConfigurationError('Invalid configuration value '
                                 'for "{0}"'.format(key))


def includeme(config):

    settings = config.registry.settings
    key = 'filterwarnings.category'
    warnings.filterwarnings(settings.get('filterwarnings.action', 'ignore'),
                            settings.get('filterwarnings.message', ''),
                            get_category(settings, key),
                            settings.get('filterwarnings.module', '')
                            )

    index = 1
    while True:
        prefix = 'filterwarnings.{0}'.format(index)
        action = settings.get('{0}.action'.format(prefix))
        if not action:
            break
        key = '{0}.category'.format(prefix)
        warnings.filterwarnings(action,
                                settings.get('{0}.message'.format(prefix), ''),
                                get_category(settings, key),
                                settings.get('{0}.module'.format(prefix), ''),
                                append=True
                                )
        index += 1
