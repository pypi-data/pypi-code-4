# Test runner with no database creation
TEST_RUNNER = 'pygmy.tests.testrunner.DatabaselessTestRunner'

SECRET_KEY = 'foo'

INSTALLED_APPS = (
    'pygmy.tests',
    'pygmy',
)
