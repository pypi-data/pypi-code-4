# -*- coding: utf-8 -*-
# Django settings for kiwi project.

DEBUG = False
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    #('You', 'your@email.com'),
)
MANAGERS = ADMINS

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

SITE_ID = 2

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '/home/django/projects/kiwi_project/examplesite/site_medias/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '../examplesite/site_medias/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/site_medias/admin/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'lk4ite)aw&v)31^6tp9750p&w&3-u=t0-ingk2s$7^heox%10%'

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
    'pagination.middleware.PaginationMiddleware',
)

ROOT_URLCONF = 'examplesite.urls'

TEMPLATE_DIRS = (
    '/home/django/projects/kiwi_project/kiwi/templates/',
)

INSTALLED_APPS = (
    'kiwi',
    'pagination',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
)
