# -*- coding: utf-8 -*-
"""Module defining the requirements doctests test suite"""

import doctest
import unittest

from plone.testing import layered

from stxnext.grayscale.tests import base

def test_suite():
    suite = unittest.TestSuite()
    suite.addTests([
        layered(doctest.DocFileSuite(
                'tests/grayscale.txt',
                package='stxnext.grayscale',
                optionflags=doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS),
                layer=base.INTEGRATION_TESTING),
        ])
    return suite
