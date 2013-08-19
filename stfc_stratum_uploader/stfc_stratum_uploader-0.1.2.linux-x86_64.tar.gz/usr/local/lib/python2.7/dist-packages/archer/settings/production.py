# noinspection PyUnresolvedReferences
import re
from archer.settings.common import Common


class Production(Common):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': '%s/db/uploader.sqlite3' % Common.PROJECT_ROOT,  # Or path to database file if using sqlite3.
            'USER': '',  # Not used with sqlite3.
            'PASSWORD': '',  # Not used with sqlite3.
            'HOST': '',  # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',  # Set to empty string for default. Not used with sqlite3.
        }
    }
    @classmethod
    def load_cfg(cls):
        import ConfigParser
        import os

        def cast(value):
            if value.isdigit():
                return int(value)
            elif value.lower() in ('true', 'false'):
                return value.lower() == 'true'
            else:
                return value

        def set(option, value):
            setattr(cls, option.upper(), value)

        OPTIONS_AVAILABLE = {
            'path': ['PROJECT_ROOT', 'MEDIA_ROOT', 'STATIC_ROOT'],
            'url': ['HOSTNAME', 'MEDIA_URL', 'STATIC_URL'],
            'security': ['SECRET_KEY', 'CSRF_MIDDLEWARE_SECRET', 'ALLOWED_HOSTS'],
            'debug': ['DEBUG', 'TEMPLATE_DEBUG', 'VIEW_TEST', 'INTERNAL_IPS', 'SKIP_CSRF_MIDDLEWARE'],
            'misc': None,
        }
        LIST_TYPES = (
            ('debug', 'INTERNAL_IPS',),
            ('security', 'ALLOWED_HOSTS',),
        )

        config = ConfigParser.SafeConfigParser()
        config.read(['/etc/uploader.cfg', os.path.expanduser('~/.uploader.cfg'), './archer/settings/production.cfg'])
        for section in config.sections():
            if section == 'database':
                default_db = {}
                for option in config.options(section):
                    default_db[option.upper()] = config.get(section, option)
                set('DATABASE', {'default': default_db})
            elif section == 'logging':
                print 'TBD'
            else:
                if section not in OPTIONS_AVAILABLE.keys():
                    raise ValueError('Unrecognized section: [%s]. Perhaps, [misc] should be used instead.' % section)

                for option in config.options(section):
                    option = option.upper()
                    if OPTIONS_AVAILABLE[section] is not None and option not in OPTIONS_AVAILABLE[section]:
                        raise ValueError('Option "%s" is not available for section [%s]' % (option, section))
                    value = config.get(section, option)

                    if (section, option,) in LIST_TYPES:
                        set(option, tuple(re.split(',\s*', value)))
                    else:
                        set(option, cast(value))
