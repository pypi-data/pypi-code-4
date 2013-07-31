from .development import *


DATABASES['default']['NAME'] = '{{ app }}'
DATABASES['default']['USER'] = '{{ app }}'
DATABASES['default']['PASSWORD'] = '{{ app }}'
DATABASES['default']['ENGINE'] = 'django.db.backends.postgresql_psycopg2'
DATABASES['default']['OPTIONS'] = {
    'autocommit': True,
}
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

SECRET_KEY = 'local'

INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
INTERNAL_IPS = ('127.0.0.1',)
