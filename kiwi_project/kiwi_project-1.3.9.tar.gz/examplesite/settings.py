# -*- coding: utf-8 -*-
# Django settings for kiwi project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('You', 'your@email.com'),
)
MANAGERS = ADMINS

# Paramètres du cache
CACHE_BACKEND = 'memcached://127.0.0.1:11211/?timeout=3600' #for memcached cache
CACHE_MIDDLEWARE_GZIP = True
CACHE_MIDDLEWARE_KEY_PREFIX = 'kiwi'
CACHE_MIDDLEWARE_SECONDS = 60 * 3

# Paramètres d'accès à la BDD
DATABASES = {
    'default': {
        'NAME': 'kiwi',
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'USER': 'django',
        'PASSWORD': 'dj4ng0',
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Paris'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'fr'

SITE_ID = 1

# Kiwi options for the default value of the argument "archive" on Wikipages (optionnal, default to True)
#WIKIPAGE_ARCHIVED_DEFAULT = False

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/django/projects/kiwi_project/examplesite/site_medias/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/site_medias/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/site_medias/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lk4ite)aw&v)31^6tp9750p&w&3-u=t0-ingk2s$7^heox%10%'

# PyWiki2Xhtml options settings (optionnal)
#PYWIKI2XHTML_CONFIGSET = {
    #'standard': {
        #'active_menu_title': False,
        #'active_wikiwords': True,
        #'active_footnotes': True,
        #'absolute_path_wikiroot': '/wiki/%s/',
        #'absolute_path_createpage': None,
    #},
    #'standard_with_summary': {
        #'active_menu_title': True,
        #'active_wikiwords': True,
        #'active_footnotes': True,
        #'absolute_path_wikiroot': '/wiki/%s/',
        #'absolute_path_createpage': None,
    #}
#}

# Relative path for Kiwi medias base directory (optionnal, default to 'kiwi/')
KIWI_MEDIA_PREFIX = 'kiwi/'

# Permet de désactiver l'archivage par révision des wikipages
#WIKIPAGE_ENABLE_ARCHIVE = False
# Permet de désactiver le choix d'archivage à chaque sauvegarde
#WIKIPAGE_ARCHIVED_DEFAULT = False

TEMPLATE_CONTEXT_PROCESSORS = (
    #'django.core.context_processors.auth', # Was for Django 1.2.x
    'django.contrib.auth.context_processors.auth', # For Django >= 1.3.x
    'django.core.context_processors.debug',
    'django.core.context_processors.request',
    'kiwi.utils.context_processors.site_urls',
)
MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'examplesite.urls'

TEMPLATE_DIRS = (
    '/home/django/projects/kiwi_project/kiwi/templates/',
)

INSTALLED_APPS = (
    'kiwi',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)
