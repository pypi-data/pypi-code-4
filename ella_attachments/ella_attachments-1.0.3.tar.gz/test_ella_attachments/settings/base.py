from os.path import abspath, join, dirname, pardir

SITE_ID = 1

PROJECT_ROOT = abspath(join(dirname(__file__), pardir))

MEDIA_ROOT = join(PROJECT_ROOT, 'media')

TEMPLATE_DIRS = (
    join(PROJECT_ROOT, 'templates'),
)

SECRET_KEY = 'test_ella_attachments'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

ROOT_URLCONF = 'ella_attachments.urls'

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.messages',
    'django.contrib.redirects',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    # Uncomment the next line to enable the admin:
    'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',

    'ella.core',
    'ella.photos',
    'ella.articles',
    'ella.positions',

    'ella_attachments',
)
