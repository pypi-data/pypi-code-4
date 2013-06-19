# encoding: utf-8
import os
from StringIO import StringIO
import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite

from Products.Archetypes.tests.atsitetestcase import ATSiteTestCase
from Products.Archetypes.tests.test_classgen import Dummy
from Products.Archetypes.tests.test_classgen import gen_dummy
from Products.Archetypes.tests.test_classgen import default_text
from Products.Archetypes.atapi import *

# ptc.setupPloneSite()

import c2.patch.filenamenormalizer


class TestHotfix(ATSiteTestCase):
    """ """

    def afterSetUp(self):
        gen_dummy()
        self._dummy = dummy = Dummy(oid='dummy')
        self._dummy.initializeArchetype()

    def test_filefieldwithfilename(self):
        obj = self._dummy
        field = obj.getField('afilefield')
        obj.setAfilefield('Blo', filename='写真.jpg')
        self.assertEqual(str(obj.getAfilefield()), 'Blo')
        self.assertEqual(field.getFilename(obj), '写真.jpg')
        # print field.download(self)

    def test_filefieldwithfilename2(self):
        obj = self._dummy
        field = obj.getField('afilefield')
        obj.setAfilefield('Blo', filename='beleza.txt')
        self.assertEqual(str(obj.getAfilefield()), 'Blo')
        self.assertEqual(field.getFilename(obj), 'beleza.txt')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestHotfix))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
