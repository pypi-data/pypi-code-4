##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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

import re
import doctest
import zc.buildout.testing
from zope.testing import renormalizing


def easy_install_SetUp(test):
    zc.buildout.testing.buildoutSetUp(test)


def test_suite():
    return doctest.DocFileSuite(
        'webapp.txt',
        setUp=easy_install_SetUp,
        tearDown=zc.buildout.testing.buildoutTearDown,
        optionflags=doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE,
        checker=renormalizing.RENormalizing([
                zc.buildout.testing.normalize_endings,
                zc.buildout.testing.normalize_script,
                zc.buildout.testing.normalize_egg_py,
                (re.compile('Running .*python.* setup.py'), 'Running python setup.py'),
                (re.compile(r'\\'), '/') #windows path happiness
                ]))
