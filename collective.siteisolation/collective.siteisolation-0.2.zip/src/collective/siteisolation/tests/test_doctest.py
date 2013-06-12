# -*- coding: utf-8 -*-
import unittest
import doctest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.NORMALIZE_WHITESPACE)


def test_suite():
    suites = [Suite('traverser.txt',
               optionflags=OPTIONFLAGS,
               package='collective.siteisolation.tests')]
    return unittest.TestSuite(suites)
