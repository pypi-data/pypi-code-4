from sh.settings.base import ROOTPATH, MIDDLEWARE_CLASSES, INSTALLED_APPS

DEBUG=True
TEMPLATE_DEBUG=DEBUG

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ROOTPATH + '/project.db'
    }
}
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake'
    }
}

#Django debug toolbar

EMAIL_HOST_USER = 'EMAIL'
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'