# Test runner with no database creation
TEST_RUNNER = 'django_pygmy.tests.testrunner.DatabaselessTestRunner'

SECRET_KEY = 'foo'

INSTALLED_APPS = (
    'django_pygmy.tests',
    'django_pygmy',
)
