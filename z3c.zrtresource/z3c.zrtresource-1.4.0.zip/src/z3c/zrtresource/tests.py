##############################################################################
#
# Copyright (c) 2006 Lovely Systems and Contributors.
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
"""Tag test setup

$Id$
"""
__docformat__ = "reStructuredText"

import doctest
import unittest
import zope.component
from zope.testing import cleanup
from zope.traversing import testing
from zope.traversing.interfaces import ITraversable
from zope.traversing.namespace import view


def setUp(test):
    cleanup.setUp()
    testing.setUp()
    zope.component.provideAdapter(view, (None, None), ITraversable, name="view")
    zope.component.provideAdapter(zope.browserresource.file.FileETag)


def tearDown(test):
    cleanup.tearDown()


def test_suite():
    optionflags = (doctest.NORMALIZE_WHITESPACE
                   | doctest.ELLIPSIS
                   | doctest.REPORT_NDIFF)
    return unittest.TestSuite((
        doctest.DocFileSuite('README.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=optionflags,
                     ),
        doctest.DocFileSuite('zcml.txt',
                     setUp=setUp,
                     tearDown=tearDown,
                     optionflags=optionflags,
                     ),
        ))
