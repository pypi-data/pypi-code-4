##############################################################################
#
# Copyright (c) 2006 Zope Corporation. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Visible Source
# License, Version 1.0 (ZVSL).  A copy of the ZVSL should accompany this
# distribution.
#
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Unit tests

"""
__docformat__ = "reStructuredText"

import doctest
import os.path
import unittest

import zope.app.testing.functional
from zope.app.testing.functional import FunctionalDocFileSuite

here = os.path.realpath(os.path.dirname(__file__))

SourceFactoryLayer = zope.app.testing.functional.ZCMLLayer(
            os.path.join(here, "ftesting.zcml"), __name__, "SourceFactoryLayer")


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(doctest.DocFileSuite('README.txt'))
    suite.addTest(doctest.DocFileSuite('mapping.txt'))
    suite.addTest(doctest.DocFileSuite('constructors.txt'))
    adapters = FunctionalDocFileSuite('adapters.txt')
    adapters.layer = SourceFactoryLayer
    suite.addTest(adapters)
    return suite
