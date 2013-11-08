# -*- coding: utf-8 -*-

import unittest
from megrok.z3ctable import tests
from zope.testing import doctest


def make_test(dottedname):
    test = doctest.DocTestSuite(
        dottedname, setUp=tests.siteSetUp, tearDown=tests.siteTearDown,
        optionflags=doctest.ELLIPSIS+doctest.NORMALIZE_WHITESPACE)
    test.layer = tests.megrokZ3ctableLayer(tests)
    return test


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt', globs={'__name__': 'megrok.z3ctable'},
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    readme.layer = tests.megrokZ3ctableLayer(tests)
    suite.addTest(readme)
    for name in ['views', 'implicit', 'adapters']:
        dottedname = dottedname = 'megrok.z3ctable.tests.%s' % name
        suite.addTest(make_test(dottedname))
    return suite
