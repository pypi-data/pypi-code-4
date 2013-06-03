###############################################################
# vs.org (C) 2011, Veit Schiele
################################################################


import unittest2

from zope.component import getUtility
import zope.schema.interfaces

from base import TestBase

class InstitutionTests(TestBase):

    def _makeOne(self):
        self.portal.invokeFactory('Institution', id='zopyxgroup')
        return self.portal['zopyxgroup']

    def testCatalogSetup(self):
        catalog = self.portal.portal_catalog
        indexes = catalog.indexes()
        self.assertEqual('position' in indexes, True)
        self.assertEqual('BusinessArea' in indexes, True)
        self.assertEqual('lastname' in indexes, True)
        schema = catalog.schema()
        self.assertEqual('position' in schema, True)
        self.assertEqual('BusinessArea' in schema, True)
        self.assertEqual('lastname' in schema, True)

    def testSetupPropertysheet(self):
        self.assertEqual('vsorg_properties' in self.portal.portal_properties.objectIds(), True)
        vsorg_properties = self.portal.portal_properties.vsorg_properties.objectIds()
#        self.assertEqual('numberRegex' in vsorg_properties, True)

    def testCreateInstitution(self):
        self.login()
        inst = self._makeOne()
        self.assertEqual(inst.portal_type, 'Institution')
        self.assertEqual(len(inst.getNumbersFiltered()), 0)

    def testNumbers(self):
        self.login()
        inst = self._makeOne()
        numbers = [
                dict(number='0049-30-8185667-1'),
                dict(number='foo'),
                ]
        inst.setNumbers(numbers)

    def testGoogleMapsViews(self):
        self.login()
        inst = self._makeOne()
        inst.REQUEST['ACTUAL_URL'] = 'http://foo' # workaround

        js_view = inst.restrictedTraverse('@@maps.js', None)
        self.assertEqual(js_view is not None, True)
        html = js_view()

        view = inst.restrictedTraverse('@@map', None)
        self.assertEqual(view is not None, True)
        html = view()


class InstitutionPortletTests(TestBase):

    def _makeOne(self):
        self.portal.invokeFactory('Institution', id='zopyxgroup', title='zopyx group')
        return self.portal['zopyxgroup']

    def testVocabulary(self):
        self.login()
        # The vocabulary factory
        service = getUtility(zope.schema.interfaces.IVocabularyFactory, name='source_institutions')
        # no institutions so far
        vocabulary = service(self.portal)
        self.assertEqual(len(vocabulary), 0)
        # create an institution and then check the lenght of the vocabulary
        inst = self._makeOne()
        vocabulary = service(self.portal)
        self.assertEqual(len(vocabulary), 1)
        first_term = [x for x in vocabulary][0] # should point to ZG institution
        self.assertEqual(first_term.title, 'zopyx group')
        self.assertEqual(first_term.token, inst.UID())


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(InstitutionTests))
    suite.addTest(makeSuite(InstitutionPortletTests))
    return suite
