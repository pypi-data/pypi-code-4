# -*- coding: utf-8 -*-

import sys
import os.path

try:
    from settings_local import *
except ImportError:
    print "Don't forget create settings_local.py"

ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, ROOT)
sys.path.append(os.path.join(ROOT, '..'))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

SITE_ID = 1

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
)

SECRET_KEY = 'SECKEY'
ROOT_URLCONF = 'urls'
WSGI_APPLICATION = 'wsgi.application'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'south',
    'factory',
    'cart',
    'paymecash',
)

SOUTH_TESTS_MIGRATE = False
SKIP_SOUTH_TESTS = True

INTERNAL_IPS = [
    'localhost',
    '127.0.0.1',
]

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_DIRS = (
    os.path.join(ROOT, 'templates'),
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(funcName)s %(message)s'
        }
    },
    'handlers': {
        'paymecash': {
            'level': 'DEBUG',
            'class': 'logging.handlers.WatchedFileHandler',
            'filename': os.path.join(ROOT, 'paymecash.log'),
            'formatter': 'verbose'
        }
    },
    'loggers': {
        'paymecash': {
            'handlers': ['paymecash'],
            'level': 'ERROR',
            'propagate': True
        }
    }
}

try:
    from settings_local import *
except ImportError:
    pass