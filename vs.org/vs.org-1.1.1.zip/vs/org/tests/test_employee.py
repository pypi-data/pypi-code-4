# -*- coding: iso-8859-15-*-

################################################################
# vs.org (C) 2011, Veit Schiele
################################################################


import unittest2
from base import TestBase

class EmployeeTests(TestBase):

    def _makeOne(self):
        self.portal.invokeFactory('Institution', id='veitschielecommunications')
        inst = self.portal['veitschielecommunications']
        inst.invokeFactory('Department', id='veitschiele')
        dept = inst['veitschiele']
        dept.invokeFactory('Employeefolder', id='carstenraddatz')
        employees = dept['carstenraddatz']
        employees.invokeFactory('Employee', id='craddatz', title=u'Carsten Raddatz')
        return employees['craddatz']

    def testCreateEmployee(self):
        self.login()
        employee = self._makeOne()
        self.assertEqual(employee.portal_type, 'Employee')

    def testEmployeeVCardView(self):
        self.login()
        employee = self._makeOne()
        vcard_view = employee.restrictedTraverse('@@vcard_view')
        vcard = vcard_view()
        self.assertEqual(vcard.startswith('BEGIN:VCARD'), True)
        self.assertEqual(vcard.endswith('END:VCARD\r\n'), True)

    def testEmployeFolderView(self):
        self.login()
        employee = self._makeOne()
        employee.REQUEST['ACTUAL_URL'] = 'http://foo' # workaround
        employeefolder = employee.aq_parent
        self.assertEqual(employeefolder.portal_type, 'Employeefolder')
        view = employeefolder.restrictedTraverse('@@employeefolder_view')
        result = view()


def test_suite():
    from unittest2 import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(EmployeeTests))
    return suite
