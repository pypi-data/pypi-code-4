# -*- coding: utf-8 -*-
#
# File: PM_Task.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Michael Launay <michaellaunay@ecreall.com>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.projectmanager.config import *

##code-section module-header #fill in your manual code here
from Products.CMFCore.utils import getToolByName
##/code-section module-header

schema = Schema((

    TextField(
        name='mIntroduction',
        allowable_content_types=('text/plain', 'text/structured', 'text/html', 'application/msword',),
        widget=RichWidget(
            label="Introduction",
            label_msgid="PM_Task_Introduction_label",
            description="Presentation of the task",
            description_msgid="PM_Task_Introduction_description",
            i18n_domain='projectmanager',
        ),
        default_output_type='text/html',
        write_permission="Modify portal content",
        read_permission="View",
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PM_Task_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PM_Task(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPM_Task)

    meta_type = 'PM_Task'
    _at_rename_after_creation = True

    schema = PM_Task_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('guardFinish')
    def guardFinish(self):
        """Check if all sub action are finished
        """
        portal_workflow = getToolByName(self, 'portal_workflow')
        getInfoFor = portal_workflow.getInfoFor
        objects = self.objectValues(['PM_Action'])
        for obj in objects:
            state = getInfoFor(obj, 'review_state')
            if state not in ('finished', 'cancelled'):
                return False
        return True


registerType(PM_Task, PROJECTNAME)
# end of class PM_Task

##code-section module-footer #fill in your manual code here
##/code-section module-footer



