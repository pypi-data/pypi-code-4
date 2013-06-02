# Django settings for eukalypse_now project.
import os
PROJECT_ROOT = os.path.normpath(os.path.dirname(__file__))
HOME = os.path.expanduser("~")

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS

import djcelery
djcelery.setup_loader()

BROKER_URL = 'django://'

CELERYBEAT_SCHEDULER = 'djcelery.schedulers.DatabaseScheduler'

EUKALYPSE_BROWSER='phantomjsbin'
EUKALYPSE_HOST='http://localhost:4444'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': os.path.join(HOME , '.eukalypse_now/eukalypse_now.db'),                      # Or path to database file if using sqlite3.
        'USER': '',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

SITE_URL = 'http://localhost:8000'

NOTIFY_MAIL_SENDER = ''

TIME_ZONE = 'Europe/Berlin'
LANGUAGE_CODE = 'de-de'

SITE_ID = 1
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(HOME, 'media/')
MEDIA_URL = SITE_URL + '/media/'

TWITTER_BOOTSTRAP_ROOT = os.path.join(PROJECT_ROOT, '../bootstrap/')

STATIC_ROOT =  os.path.join(PROJECT_ROOT, 'static/')
STATIC_URL = SITE_URL + '/static/'
STATICFILES_DIRS = (
    os.path.join(PROJECT_ROOT, 'static_'),
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '2g_ey2eo0#_m(4czlumohf-(f)!je)8a%vq9wvc5rz0v%4dzw8'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "eukalypse_now.context_processors.site",
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eukalypse_now.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'eukalypse_now.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT, 'templates'),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'gunicorn',
    'south',
    'eukalypse_now',
    'easy_thumbnails',
    'djcelery',
    'kombu.transport.django',
)


THUMBNAIL_ALIASES = {
    '': {
        'detail': {'size': (100, 80)},
    },
}


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
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


# Mail server configuration

# For more information check Django's documentation:
#  https://docs.djangoproject.com/en/1.3/topics/email/?from=olddocs#e-mail-backends
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_HOST_PASSWORD = ''
EMAIL_HOST_USER = ''
EMAIL_PORT = 25
EMAIL_USE_TLS = False
