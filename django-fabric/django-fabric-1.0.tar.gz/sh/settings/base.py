# -*- coding: utf-8 -*-
import os

ROOTPATH = os.path.dirname(os.path.dirname(__file__))
DEBUG_TOOLBAR = False

ADMINS = (
    ('Rolf Erik Lekang', 'me@rolflekang.com'),
    ('Ole Rønning', 'ole@myessential.net'),
)

MANAGERS = ADMINS

TIME_ZONE = 'Europe/Oslo'
LANGUAGE_CODE = 'nb'
LANGUAGES = (
    ('nb', 'Norsk'),
    ('en', 'English')
)
LOCALE_PATHS = (
    os.path.join(ROOTPATH, '../locale'),
)

SITE_URL = 'http://www.starthjelpa.no'
FRONTPAGE_ID = 1

ANALYTICS = True
ANALYTICS_TRACK_ADMINS = False
ANALYTICS_CODE = 'UA-32144222-4'

SITE_ID = 1
USE_I18N = True

MEDIA_ROOT = os.path.join(ROOTPATH, 'files/uploads')
STATIC_ROOT = os.path.join(ROOTPATH, 'static')


MEDIA_URL = '/uploads/'
STATIC_URL = '/static/'

CKEDITOR_UPLOAD_PATH = os.path.join(MEDIA_ROOT,"images")
CKEDITOR_UPLOAD_PREFIX = "/uploads/images/"
CKEDITOR_CONFIGS = {
    'default': {
        'height': 500,
        'width': 730,
        'toolbar': [
            ['Format', 'Bold', 'Italic', 'Underline','Image', 'NumberedList','BulletedList','-','Outdent','Indent', 'Link','Unlink', 'Table', 'Preview',],
            ],
        },


    }

# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(ROOTPATH, 'files/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

SECRET_KEY = 'p0otu-kbp!y74po$#kmpyd)6tx4)kq!u&)5g9jz8h)-$bnzav*'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'sh.core.auth.LocalUserMiddleware',
)

ROOT_URLCONF = 'sh.urls'

TEMPLATE_DIRS = (
    os.path.join(ROOTPATH, "templates"),
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.markup',

    'south',
    'sorl.thumbnail',
    'ckeditor',

    'sh.core',

    'sh.app.dashboard',
    'sh.app.pages',
    'sh.app.news',

)

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
