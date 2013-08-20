import os
import configurations.importer

configurations.importer.install()

from common import Common
from dev import Dev
from production import Production
from test import Test, PostgresCI, SqliteCI

if os.environ['DJANGO_CONFIGURATION'] == 'Production':
    Production.load_cfg()
# hack is needed to make sniffer/nosetests command work with django-configurations plugin
elif os.environ['DJANGO_CONFIGURATION'] == 'Test':
    ANONYMOUS_USER_ID = Test.ANONYMOUS_USER_ID
    SOUTH_TESTS_MIGRATE = Test.SOUTH_TESTS_MIGRATE
    INSTALLED_APPS = Test.INSTALLED_APPS
    TEST_RUNNER = Test.TEST_RUNNER
    SECRET_KEY = Test.SECRET_KEY
    DATABASES = Test.DATABASES
    TEST_RUNNER = Test.TEST_RUNNER
    PASSWORD_HASHERS = Test.PASSWORD_HASHERS
    DEFAULT_FILE_STORAGE = Test.DEFAULT_FILE_STORAGE
