# noinspection PyUnresolvedReferences
import os
from configurations import importer

importer.install()

from archer.settings.common import Common


class Test(Common):
    DEBUG = True
    TEMPLATE_DEBUG = DEBUG
    # in memory doesn't work for nosetests
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST_NAME': ':memory:',
        },
    }

    # syncdb should be faster than using South migrations
    SOUTH_TESTS_MIGRATE = False

    INSTALLED_APPS = Common.INSTALLED_APPS + (
        'django_nose',
    )

    TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'

    # Use weak hashes to increase tests speed
    PASSWORD_HASHERS = (
        'django.contrib.auth.hashers.MD5PasswordHasher',
    )

    DEFAULT_FILE_STORAGE = 'inmemorystorage.InMemoryStorage'


class PostgresCI(Test):
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql_psycopg2',
            # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'uploader_ci_test', # Or path to database file if using sqlite3.
            'USER': 'postgres', # Not used with sqlite3.
            'PASSWORD': '', # Not used with sqlite3.
            'HOST': '127.0.0.1', # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '', # Set to empty string for default. Not used with sqlite3.
        },

    }


class SqliteCI(Test):
    DEBUG = True
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'TEST_NAME': ':memory:',
        },
    }
