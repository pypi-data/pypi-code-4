# -*- coding: utf-8 -*-
from collective.pdfpeek import testing
from plone.testing import layered
import doctest
import unittest2 as unittest

integration_tests = [
    'integration.txt'
]
functional_tests = [
]


def test_suite():
    return unittest.TestSuite(
        [layered(doctest.DocFileSuite('tests/%s' % f,
                                      package='collective.pdfpeek',
                                      optionflags=testing.optionflags),
                 layer=testing.PDFPEEK_INTEGRATION_TESTING)
            for f in integration_tests]
        +
        [layered(doctest.DocFileSuite('tests/%s' % f,
                                      package='collective.pdfpeek',
                                      optionflags=testing.optionflags),
                 layer=testing.PDFPEEK_FUNCTIONAL_TESTING)
            for f in functional_tests]
    )
