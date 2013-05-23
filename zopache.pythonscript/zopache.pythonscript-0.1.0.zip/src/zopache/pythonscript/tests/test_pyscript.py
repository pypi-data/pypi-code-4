##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Basic tests for Page Templates used in content-space.
"""
import unittest
from zope.interface.verify import verifyClass

from zopache.pythonscript.interfaces import IPythonScript
from zopache.pythonscript.pythonscript import PythonScript, Sized


class PythonScriptTests(unittest.TestCase):

    def testInterface(self):
        self.failUnless(IPythonScript.implementedBy(PythonScript))
        self.failUnless(verifyClass(IPythonScript, PythonScript))

    def test_call(self):
        ps = PythonScript()
        ps.signature = u'name'
        ps.source = u'return "Hello %s!" %name'
        ps.__name__ = u'hello'
        self.assertEqual(ps('Chris'), 'Hello Chris!')


class DummyScript(object):

    def __init__(self, source):
        self.source = source

    def getSource(self):
        return self.source

class SizedTests(unittest.TestCase):

    def testInterface(self):
        from zope.size.interfaces import ISized
        self.failUnless(ISized.implementedBy(Sized))
        self.failUnless(verifyClass(ISized, Sized))

    def test_zeroSized(self):
        s = Sized(DummyScript(''))
        self.assertEqual(s.sizeForSorting(), ('line', 0))
        self.assertEqual(s.sizeForDisplay(), u'0 lines')

    def test_oneSized(self):
        s = Sized(DummyScript('one line'))
        self.assertEqual(s.sizeForSorting(), ('line', 1))
        self.assertEqual(s.sizeForDisplay(), u'1 line')

    def test_arbitrarySize(self):
        s = Sized(DummyScript('some line\n'*5))
        self.assertEqual(s.sizeForSorting(), ('line', 5))
        self.assertEqual(s.sizeForDisplay(), u'5 lines')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(PythonScriptTests),
        unittest.makeSuite(SizedTests),
        ))
