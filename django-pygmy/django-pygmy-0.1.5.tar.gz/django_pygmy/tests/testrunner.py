from django.test.simple import DjangoTestSuiteRunner


class DatabaselessTestRunner(DjangoTestSuiteRunner):
    """ A test runner to test without database creation """

    def setup_databases(self):
        """ Override the database creation defined in parent class """
        pass

    def teardown_databases(self, *args):
        """ Override the database teardown defined in parent class """
        pass
