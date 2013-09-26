# -*- coding: utf-8 -*-
#
# File: testPM_ProjectManager.py
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
from Products.projectmanager.content.PM_ProjectManager import PM_ProjectManager

##code-section module-beforeclass #fill in your manual code here
import email
from Products.MailHost.MailHost import MailHost as MailBase

class MockMailHost(MailBase):
        """A MailHost that collects messages instead of sending them.
           From Plone-2.5.5/PasswordResetTool/tests/utils/mailhost.py
        """

        def __init__(self, id):
            MailBase.__init__(self, id)
            self.reset()

        def reset(self):
            self.messages = []

        def send(self, message, mto=None, mfrom=None, subject=None, encode=None):
            """
            Basically construct an email.Message from the given params to make sure
            everything is ok and store the results in the messages instance var.
            """

            message = email.message_from_string(message)
            message['To'] = mto
            message['From'] = mfrom
            message['Subject'] = subject

            self.messages.append(message)
            self._p_changed = True

##/code-section module-beforeclass


class testPM_ProjectManager(testPlone):
    """Test-cases for class(es) ."""

    ##code-section class-header_testPM_ProjectManager #fill in your manual code here
    ##/code-section class-header_testPM_ProjectManager

    def afterSetUp(self):
        self.portal_workflow = self.portal.portal_workflow
        self.members = []
        self.membership = self.portal.portal_membership
        self.membership.addMember("aUser", "passwd", ['Member'], [], properties={'name': 'Mr User', 'email': 'aUser@example.com'})
        member = self.membership.getMemberById("aUser")
        self.members.append(member)
        self.membership.addMember("aManager", "passwd", ['Manager'], [], properties={'name': 'Mr Manager', 'email': 'aManager@example.com'})
        member = self.membership.getMemberById("aManager")
        self.members.append(member)
        self.membership.addMember("aReviewer", "passwd", ['Reviewer'], [], properties={'name': 'Mr Member', 'email': 'aReviewer@example.com'})
        member = self.membership.getMemberById("aReviewer")
        self.members.append(member)
        self.portal_groups = self.portal.portal_groups
        self.login('aManager')
        myproject = self.portal.invokeFactory('PM_ProjectManager', 'myproject')
        self.mProject = self.portal[myproject]
        self.portal_workflow.doActionFor(self.mProject, "publish")
        state = self.portal_workflow.getInfoFor(self.mProject, 'review_state')
        self.assertEqual(state, 'published')
        self.portal._original_MailHost = self.portal.MailHost
        self.portal.MailHost = MockMailHost('MailHost')
        pass
    def test_getHumanResources(self):
        self.login('aManager')
        pm = self.mProject
        members = pm.getHumanRessources()
        self.failUnless([m for m in members if m[0] not in [x.getId() for x in self.members]])

    # Manually created methods


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testPM_ProjectManager))
    return suite

##code-section module-footer #fill in your manual code here
##/code-section module-footer

if __name__ == '__main__':
    framework()


