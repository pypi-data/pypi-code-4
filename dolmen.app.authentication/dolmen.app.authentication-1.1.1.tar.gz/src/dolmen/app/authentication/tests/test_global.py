# -*- coding: utf-8 -*-

import re
import doctest
import unittest

from dolmen.app.authentication import tests
from zope.app.wsgi.testlayer import BrowserLayer
from zope.testing import renormalizing


FunctionalLayer = BrowserLayer(tests)


checker = renormalizing.RENormalizing([
    # Accommodate to exception wrapping in newer versions of mechanize
    (re.compile(r'httperror_seek_wrapper:', re.M), 'HTTPError:')])


def test_suite():
    suite = unittest.TestSuite()
    files = ('../README.txt',)
    for filename in files:
        docfile = doctest.DocFileSuite(
            filename,
            checker=checker,
            globs={
                'getRootFolder': FunctionalLayer.getRootFolder,
                '__name__': 'dolmen.app.authentication.tests'},
            optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
        docfile.layer = FunctionalLayer
        suite.addTest(docfile)
    return suite
