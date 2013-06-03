################################################################
# vs.org (C) 2011, Veit Schiele
################################################################


import unittest2
from AccessControl.SecurityManagement import newSecurityManager
from base import TestBase

class DepartmentTests(TestBase):

    def _makeOne(self):
        self.portal.invokeFactory('Institution', id='zopyxgroup')
        inst = self.portal['zopyxgroup']
        inst.invokeFactory('Department', id='banality')
        return inst['banality']

    def testCreateDepartment(self):
        self.login()
        dept = self._makeOne()
        self.assertEqual(dept.portal_type, 'Department')

    def testCreateDepartmentOutsideInstitution(self):
        self.login()
        # raises ValueError(Disallowed portal_type ..)
        with self.assertRaises(ValueError):
            self.portal.invokeFactory('Department', id='banality')



def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(DepartmentTests))
    return suite
