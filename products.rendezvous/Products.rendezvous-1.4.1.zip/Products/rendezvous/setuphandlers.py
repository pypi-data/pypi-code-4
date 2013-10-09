# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by Ecreall
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Vincent Fretin <vincentfretin@ecreall.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('rendezvous: setuphandlers')
from Products.rendezvous.config import PROJECTNAME
from Products.rendezvous.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotrendezvousProfile(context):
    return context.readDataFile("rendezvous_marker.txt") is None

def setupHideTypesFromSearch(context):
    """hide selected classes in the search form"""
    if isNotrendezvousProfile(context): return 
    # XXX use https://svn.plone.org/svn/collective/DIYPloneStyle/trunk/profiles/default/properties.xml
    site = context.getSite()
    portalProperties = getToolByName(site, 'portal_properties')
    siteProperties = getattr(portalProperties, 'site_properties')
    for klass in ['RDV_Proposition']:
        propertyid = 'types_not_searched'
        lines = list(siteProperties.getProperty(propertyid) or [])
        if klass not in lines:
            lines.append(klass)
            siteProperties.manage_changeProperties(**{propertyid: lines})

def setupHideMetaTypesFromNavigations(context):
    """hide selected classes in the search form"""
    if isNotrendezvousProfile(context): return 
    # XXX use https://svn.plone.org/svn/collective/DIYPloneStyle/trunk/profiles/default/properties.xml
    site = context.getSite()
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    for klass in ['RDV_Proposition']:
        propertyid = 'metaTypesNotToList'
        lines = list(navtreeProperties.getProperty(propertyid) or [])
        if klass not in lines:
            lines.append(klass)
            navtreeProperties.manage_changeProperties(**{propertyid: lines})



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotrendezvousProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotrendezvousProfile(context): return
    site = context.getSite()



##code-section FOOT
##/code-section FOOT
