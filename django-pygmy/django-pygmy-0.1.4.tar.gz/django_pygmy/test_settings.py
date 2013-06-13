DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

MEDIA_URL = ''
STATIC_URL = ''

SECRET_KEY = 'foo'

INSTALLED_APPS = (
    'django_pygmy.tests',
    'django_pygmy',
)
