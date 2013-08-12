# Django settings for testing project.

import os

from .base import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG

for db in DATABASES.values():
    db['ENGINE'] = 'django.db.backends.sqlite3'
    db['NAME'] = ':memory:'

INSTALLED_APPS = INSTALLED_APPS + ('django_coverage',)
     
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}

EMAIL_BACKEND = 'django.core.mail.backends.dummy.EmailBackend'

SENDSMS_BACKEND = 'sendsms.backends.dummy.SmsBackend'

SOUTH_TESTS_MIGRATE = False

COVERAGE_REPORT_HTML_OUTPUT_DIR = os.path.join(DIRNAME, 'reports')
COVERAGE_MODULE_EXCLUDES = ['tests$', 'settings$', 'urls$', 'locale$',
                            'common.views.test', 'django',
                            'migrations']
COVERAGE_MODULE_EXCLUDES.extend(['management'])

USE_CELERY = False
CELERY_ALWAYS_EAGER = True
try:
    import djcelery #@UnresolvedImport
    djcelery.setup_loader()
except:
    pass

LOGGING = {
    'version': 1,
    'handlers': {
        'null': {
            'class':'django.utils.log.NullHandler',
        },
    },
    'loggers': {
        '': {
            'handlers': ['null']
        }
    }
}

INSTALLED_APPS = tuple(item for item in INSTALLED_APPS
                       if item not in ['debug_toolbar']
                      )

MIDDLEWARE_CLASSES = tuple(item for item in MIDDLEWARE_CLASSES
                           if item not in ['debug_toolbar.middleware.DebugToolbarMiddleware']
                          )
