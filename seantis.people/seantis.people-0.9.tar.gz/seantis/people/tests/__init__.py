from plone import api

from zope.security.management import newInteraction, endInteraction

from seantis.plonetools.testing import TestCase
from seantis.people.testing import (
    INTEGRATION_TESTING,
    FUNCTIONAL_TESTING
)


# to use with integration where security interactions need to be done manually
class IntegrationTestCase(TestCase):
    layer = INTEGRATION_TESTING

    def setUp(self):
        super(IntegrationTestCase, self).setUp()
        # setup security
        newInteraction()

    def tearDown(self):
        endInteraction()
        super(IntegrationTestCase, self).tearDown()

    def get_import_form(self):
        with self.user('admin'):
            obj = api.content.create(
                id='people',
                type='seantis.people.list',
                container=self.new_temporary_folder()
            )

            return api.content.get_view('import', obj, self.request)


# to use with the browser which does its own security interactions
class FunctionalTestCase(TestCase):
    layer = FUNCTIONAL_TESTING
