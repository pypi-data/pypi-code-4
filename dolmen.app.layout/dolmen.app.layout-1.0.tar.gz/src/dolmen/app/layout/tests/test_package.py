# -*- coding: utf-8 -*-

import doctest
import unittest
from dolmen.app.layout import tests


def interfaceDescription(interface):
    for name, attr in interface.namesAndDescriptions():
        print "%s: %s" % (name, attr.getDoc())


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        '../README.txt', globs={
            '__name__': 'dolmen.app.layout',
            'interfaceDescription': interfaceDescription,
            },
        setUp=tests.siteSetUp, tearDown=tests.siteTearDown,
        optionflags=(doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS))
    readme.layer = tests.DolmenAppLayoutLayer(tests)
    suite.addTest(readme)
    return suite
