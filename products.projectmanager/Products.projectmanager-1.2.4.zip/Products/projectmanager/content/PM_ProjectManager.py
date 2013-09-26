# -*- coding: utf-8 -*-
#
# File: PM_ProjectManager.py
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


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

PM_ProjectManager_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class PM_ProjectManager(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IPM_ProjectManager)

    meta_type = 'PM_ProjectManager'
    _at_rename_after_creation = True

    schema = PM_ProjectManager_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods

    security.declarePublic('getHumanRessources')
    def getHumanRessources(self):
        """ return the list of all concerned members
        """
        members = []
        mtool = getToolByName(self, 'portal_membership')
        members = mtool.listMembers()
        members = [ "%s: %s"%(m.getId(), m.getProperty('fullname')) for m in members]
        return members


registerType(PM_ProjectManager, PROJECTNAME)
# end of class PM_ProjectManager

##code-section module-footer #fill in your manual code here
##/code-section module-footer



