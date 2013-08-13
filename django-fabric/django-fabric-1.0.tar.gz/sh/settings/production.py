from sh.settings.base import INSTALLED_APPS

with open('/home/web/db_pw/starthjelpa', 'rb') as f:
    db_password = f.readline()
db_password = db_password.replace("\n","").strip()

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'starthjelpa',
        'USER': 'treningsportal',
        'PASSWORD': db_password,
        'HOST': '127.0.0.1',
        'PORT': ''
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        'LOCATION': '127.0.0.1:11211',
        'TIMEOUT': 86400,
        'KEY_PREFIX': 'sh',
        }
}

INSTALLED_APPS += ( 'raven.contrib.django', )

SENTRY_DSN = 'http://d3eb55dabc6549a3b1490b25adddea62:38c31922307c4c41b9b2d384059d62b6@sentry.mocco.no/3'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'root': {
        'level': 'WARNING',
        'handlers': ['sentry'],
        },
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
        },
        },
    'handlers': {
        'sentry': {
            'level': 'ERROR',
            'class': 'raven.contrib.django.handlers.SentryHandler',
            },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'django.db.backends': {
            'level': 'ERROR',
            'handlers': ['console'],
            'propagate': False,
            },
        'raven': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
            },
        'sentry.errors': {
            'level': 'DEBUG',
            'handlers': ['console'],
            'propagate': False,
            },
        },
    }
