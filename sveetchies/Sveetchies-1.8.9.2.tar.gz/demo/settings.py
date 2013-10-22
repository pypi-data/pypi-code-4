# -*- coding: utf-8 -*-
"""
Django settings for Sveetchies demo

Ce fichier est une version de développement, dans le cas d'une installation en 
production, il est conseillé de le dupliquer sous un nom tel que ``prod_settings.py``, 
de le modifier selon les besoins et n'utiliser que ce dernier (et y virer ce 
commentaire).
"""
import os
import Sveetchies

# Détermination automatiqueme des répertoires de base
# Attention la détermination auto de WEBAPP_ROOT pose problème en dehors de l'utilisation 
# avec ``django-admin runserver [..]``. Dans ce cas il faut alors spécifier manuellement 
# un chemin absolu
WEBAPP_ROOT = os.path.abspath(os.path.dirname(__file__))
SVEETCHIES_PATH_INSTALL = os.path.dirname(Sveetchies.__file__)

#####
#
#   1. À éditer à chaque nouvelle installation
#
#####

# Options de debug
DEBUG = True
TEMPLATE_DEBUG = DEBUG
UNIFORM_FAIL_SILENTLY = not DEBUG
INTERNAL_IPS = ( '192.168.0.112', )

ADMINS = (
    ('Sveetch', 'david.thenon@wanadoo.fr'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'NAME': 'sveetchies',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'django',
        'PASSWORD': 'dj4ng0',
    }
}

# Identifiant du "site" de désignation (en général 1 pour celui en développement et 2 
# celui en production, etc..)
SITE_ID = 1

# Make this unique, and don't share it with anybody.
SECRET_KEY = '$emzo7-p1^j-$s^zqo797e1-_@*hf6qxjz@93*iwr30((_ok3='

#####
#
#   2. Optionnellement éditable pour certains besoins
#
#####

# Nom du répertoire des médias, utilisé ensuite pour former les chemins absolus et url 
# relatifs de ce dernier, pas de slash de début ou de fin
MEDIA_DIRNAME = 'medias'

# URL that handles the media served from ``MEDIA_ROOT``. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
# Si vous utilisez une URL pour cette option, il faudra alors spécifier manuellement 
# en dur la valeur de ``MEDIA_ROOT``
MEDIA_URL = '/{0}/'.format(MEDIA_DIRNAME)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.join(WEBAPP_ROOT, MEDIA_DIRNAME)+"/"

# Nom du répertoire des fichiers statiques
STATIC_DIRNAME = 'static'

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/{0}/'.format(STATIC_DIRNAME)

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(WEBAPP_ROOT, STATIC_DIRNAME)+"/"

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(WEBAPP_ROOT, 'webapp_statics/'),
    os.path.join(SVEETCHIES_PATH_INSTALL, 'django/documents/static/'),
)

# URL prefix for admin media -- CSS, JavaScript and images.
# Mêmes principes que ``MEDIA_URL``
ADMIN_MEDIA_PREFIX = os.path.join('/', STATIC_DIRNAME, 'admin/')

# Chemins d'emplacement des templates, l'ordre établi sera celui de la 
# résolution/recherche des templates (d'abord dans le premier, etc..)
TEMPLATE_DIRS = (
    os.path.join(WEBAPP_ROOT, 'templates/'),
    os.path.join(SVEETCHIES_PATH_INSTALL, 'django/documents/templates/documents/'),
)

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr_FR'

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale
USE_L10N = True

# Configuration des moteurs de caches disponibles
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'sveetchies-demo',
        'TIMEOUT': 60,
        'KEY_PREFIX': 'dev',
        'OPTIONS': {
            'MAX_ENTRIES': 1000
        }
    }
}

# Map des titres de vues pour autobreadcrumbs
AUTOBREADCRUMBS_TITLES = {
    'documents-index': u'Plan du site',
    'documents-board': u'Administration des documents',
    'documents-insert-add': u'Nouveau document à insérer',
    'documents-insert-delete': u'Supprimer le document #{{ insert_instance.slug }}',
    'documents-insert-edit': u'Editer le document #{{ insert_instance.slug }}',
    'documents-page-add': u'Nouvelle page',
    'documents-page-delete': u'Supprimer la page #{{ page_instance.slug }}',
    #'documents-page-details': u'{{ page_instance.title }}',
    'documents-help': u'Aide à l\'utilisation',
    'documents-page-edit': u'Editer la page #{{ page_instance.slug }}',
    'documents-page-add-child': u'Créer une nouvelle page parente de #{{ parent_page_instance.slug }}',
}

# Settings supplémentaire pour contenir la bonne url de preview des documents
CODEMIRROR_SETTINGS = {
    'sveetchies-documents-page': {
        'mode': 'rst',
        'csrf': 'CSRFpass',
        'preview_url': ('documents-preview',),
        'quicksave_url': ('documents-page-quicksave',),
        'quicksave_datas': 'DJANGOCODEMIRROR_OBJECT',
        'lineWrapping': True,
        'lineNumbers': True,
        'help_link': ('documents-help',),
    },
    'sveetchies-documents-insert': {
        'mode': 'rst',
        'csrf': 'CSRFpass',
        'preview_url': ('documents-preview',),
        'quicksave_url': ('documents-insert-quicksave',),
        'quicksave_datas': 'DJANGOCODEMIRROR_OBJECT',
        'lineWrapping': True,
        'lineNumbers': True,
        'help_link': ('documents-help',),
    },
}

#####
#
#   3. Ne pas toucher
#
#####

# Options de la debug_toolbar
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
}
DEBUG_TOOLBAR_PANELS = (
    #'debug_toolbar_user_panel.panels.UserPanel',
    #'inserdiag_webapp.utils.debugtoolbar_filter.InserdiagVersionDebugPanel',
    #'debug_toolbar.panels.timer.TimerDebugPanel',
    'debug_toolbar.panels.settings_vars.SettingsVarsDebugPanel',
    'debug_toolbar.panels.headers.HeaderDebugPanel',
    'debug_toolbar.panels.request_vars.RequestVarsDebugPanel',
    'debug_toolbar.panels.template.TemplateDebugPanel',
    'debug_toolbar.panels.sql.SQLDebugPanel',
    #'debug_toolbar.panels.signals.SignalDebugPanel',
    #'debug_toolbar.panels.logger.LoggingPanel',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'Sveetchies.django.context_processors.site_urls',
    'Sveetchies.django.autobreadcrumbs.context_processors.AutoBreadcrumbsContext',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'demo.urls'

INSTALLED_APPS = (
    'debug_toolbar',
    'mptt',
    'uni_form',
    'Sveetchies.django.autobreadcrumbs',
    'Sveetchies.django.djangocodemirror',
    'Sveetchies.django.documents',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.markup',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    #'django.contrib.admindocs',
)

# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
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
