# -*- coding: utf-8 -*-
#
# File: testPM_Task.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Michael Launay <michaellaunay@ecreall.com>"""
__docformat__ = 'plaintext'

import os, sys
if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

##code-section module-header #fill in your manual code here
##/code-section module-header

#
# Test-cases for class(es) 
#

from Testing import ZopeTestCase
from Products.projectmanager.config import *
from Products.projectmanager.tests.testPlone import testPlone

# Import the tested classes
from Products.projectmanager.content.PM_Task import PM_Task

##code-section module-beforeclass #fill in your manual code here
##/code-section module-beforeclass


class testPM_Task(testPlone):
    """Test-cases for class(es) ."""

    ##code-section class-header_testPM_Task #fill in your manual code here
    ##/code-section class-header_testPM_Task

    def afterSetUp(self):
        pass

    # Manually created methods


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPM_Task))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


