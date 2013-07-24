# Minimal Django settings for testproject.

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:'
    }
}

INSTALLED_APPS = ('fiat',)

SECRET_KEY = 'secretkey'