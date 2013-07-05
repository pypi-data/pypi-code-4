# -*- coding: UTF-8 -*-
# Django settings for djgraph project.

import os
from csat.django.apps import base
from csat import acquisition

DEBUG = False
_ = gettext = lambda s: s

# Absolute path to the directory containing the Django project
WEBAPP_BASE = os.path.dirname(__file__)

# Absolute path to the directory containing the wsgi application
# infrastructure (nginx config, unix sockets, project code,...)
ENV_BASE = os.environ['CSAT_ENVDIR']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Chicago'

MANAGERS = ADMINS = ()

INTERNAL_IPS = ('127.0.0.1',)

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

LANGUAGES = [
    ('en', 'English'),
#    ('fr', 'French'),
]

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ENV_BASE, 'database.sqlite'),
    }
}

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(ENV_BASE, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(WEBAPP_BASE, 'static')

GRAPHS_ROOT = os.path.join(ENV_BASE, 'graphs')

EXECUTION_LOGS_ROOT = os.path.join(ENV_BASE, 'logs')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'django_assets.finders.AssetsFinder',
)

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'coffin.template.loaders.Loader',
)

JINJA2_TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

JINJA2_DISABLED_TEMPLATES = (
    r'(admin|admin_doc|debug_toolbar)/',
#    r'([^/]+.html)',
    r'(bootstrap)/'
)

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

COMPASS_PLUGINS = (
    'bootstrap-sass',
    'animation',
)

COMPASS_CONFIG = {
    'output_style': ':expanded',
    'additional_import_paths': [
        os.path.join(os.path.dirname(base.__file__), 'assets', 'sass_shared'),
    ]
}

APPEND_SLASH = True

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.doc.XViewMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    #'debug_toolbar.middleware.DebugToolbarMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}

ROOT_URLCONF = 'csat.webapp.urls'

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.request',
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'csat.visualization.context_processors.layout_workers',
)

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'djgraph.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
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
    'django.contrib.markup',
    'south',
    'coffin',
    'polymorphic',
    'django_assets',
    'crispy_forms',
    'csat.django.apps.base',
    'csat.django.apps.bootstrap',
    'csat.acquisition',
    'csat.visualization',
) + tuple(acquisition.get_django_applications())

ALLOWED_HOSTS = [
    'localhost',
]

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'filters': {},
    'formatters': {
        'verbose': {
            'format': '%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s',
        },
        'simple': {
            'format': '%(levelname)s %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}

execfile(os.path.join(ENV_BASE, 'settings.py'), globals(), locals())

from csat.django import monkeypatch
monkeypatch.patch()
