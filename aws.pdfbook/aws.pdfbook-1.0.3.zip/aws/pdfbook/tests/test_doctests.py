# -*- coding: utf-8 -*-
# $Id: test_doctests.py 117038 2010-05-07 09:47:23Z glenfant $
"""Running doctests"""

import os
import glob
import doctest
import unittest
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite
from aws.pdfbook.tests.common import PDFBookFunctionalTestCase

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests():
    this_dir = os.path.dirname(os.path.abspath(__file__))
    filenames = [filename for filename in glob.glob(os.path.join(this_dir, 'test*.txt'))]
    return filenames

def test_suite():
    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='aws.pdfbook.tests',
               test_class=PDFBookFunctionalTestCase)
         for filename in list_doctests()]
        )
