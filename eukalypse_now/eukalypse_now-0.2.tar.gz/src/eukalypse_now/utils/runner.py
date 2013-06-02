from logan.runner import run_app



CONFIG_TEMPLATE = """
import os.path

CONF_ROOT = os.path.dirname(__file__)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(CONF_ROOT, 'eukalypse_now.db'),
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}


SENTRY_DSN = ''

if SENTRY_DSN:
    LOGGING['handlers']['sentry'] ={
            'level': 'INFO',
            'class': 'raven.handlers.logging.SentryHandler',
            'dsn': SENTRY_DSN,
        }
    LOGGING['loggers']['django.request']['handlers'].append('sentry')

"""


def generate_settings():
    """
    This command is run when ``default_path`` doesn't exist, or ``init`` is
    run and returns a string representing the default data to put into their
    settings file.
    """
    import os
    HOME = os.path.expanduser("~")
    pathname = os.path.join(HOME, '.eukalypse_now/media/images')
    try:
        os.makedirs(pathname, 0755 )
    except OSError:
        print "Skipping creation of %s because it exists already or something went wrong."%pathname
    
    return CONFIG_TEMPLATE


def main():
    run_app(
        project='eukalypse_now',
        default_config_path='~/.eukalypse_now/eukalypse_now.conf.py',
        default_settings='eukalypse_now.settings',
        settings_initializer=generate_settings,
        settings_envvar='EUKALYPSE_NOW_CONF',
    )

if __name__ == '__main__':
    main()
