# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Michael Launay <michaellaunay@ecreall.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('projectmanager: setuphandlers')
from Products.projectmanager.config import PROJECTNAME
from Products.projectmanager.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotprojectmanagerProfile(context):
    return context.readDataFile("projectmanager_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotprojectmanagerProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotprojectmanagerProfile(context): return
    site = context.getSite()



##code-section FOOT
##/code-section FOOT
