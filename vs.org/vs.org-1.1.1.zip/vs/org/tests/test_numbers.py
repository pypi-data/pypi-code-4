################################################################
# vs.org (C) 2011, Veit Schiele
################################################################


import unittest2
from base import TestBase

NUMBERS = [
    dict(type='phone', number='+49 123 45678-00', externally_visible='1'),
    dict(type='fax', number='+49 123 45678-01', externally_visible='1'),
    dict(type='phone', number='+49 123 45678-98', externally_visible=''),
    dict(type='fax', number='+49 123 45678-99', externally_visible=''),
]
class NumberMixinTests(TestBase):

    def _makeOne(self, with_numbers=True):
        self.login()
        self.portal.invokeFactory('Institution', id='zopyxgroup')
        if with_numbers:
            self.portal['zopyxgroup'].setNumbers(NUMBERS)
        return self.portal['zopyxgroup']

    def testNoNumbers(self):
        institution = self._makeOne(with_numbers=False)
        self.assertEqual(len(institution.getNumbersFiltered()), 0)

    def testWithNumbers(self):
        institution = self._makeOne()
        self.assertEqual(len(institution.getNumbersFiltered()), 4)

    def testGetPhoneNumber(self):
        institution = self._makeOne()
        phone = institution.getTelephone()
        self.assertEqual(phone, '+49 123 45678-00')

    def testGetNotExistingMobile(self):
        institution = self._makeOne()
        mobile = institution.getMobile()
        self.assertEqual(mobile, None)

    def testGetNumberTypes(self):
        institution = self._makeOne()
        types = institution.getNumberTypes()
        self.assertEqual(len(types), 2)
        self.assertEqual('phone' in types, True)
        self.assertEqual('fax' in types, True)

    def getNumbersByTypeUnfiltered(self):
        institution = self._makeOne()
        numbers = institution.getNumbersByType('phone', do_filter=False)
        self.assertEqual(len(numbers), 2)

    def getNumbersByTypeUnfiltered(self):
        institution = self._makeOne()
        numbers = institution.getNumbersByType('phone', do_filter=True)
        self.assertEqual(len(numbers), 1)

def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(NumberMixinTests))
    return suite
