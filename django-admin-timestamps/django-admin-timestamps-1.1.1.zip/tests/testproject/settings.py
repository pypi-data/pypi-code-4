from os.path import dirname, join

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = join(dirname(__file__), 'db', 'admintimestamps.db')

DATABASES = {
    "default": {
        "ENGINE": 'django.db.backends.sqlite3',
        "NAME": join(dirname(__file__), 'db', 'admintimestamps.db')
    }
}

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'admintimestamps',
    'testproject',
)

SECRET_KEY = 'secret'

ROOT_URLCONF = 'testproject.urls'
