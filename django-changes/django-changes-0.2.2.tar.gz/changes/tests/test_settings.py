INSTALLED_APPS = (
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'changes',
    'changes.tests'
)

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3'
    }
}

SECRET_KEY = 'none'

USE_TZ = True
