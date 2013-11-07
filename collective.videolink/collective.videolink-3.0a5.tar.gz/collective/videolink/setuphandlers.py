# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.4.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """David Bain <david.bain@alteroo.com>, based on work done by AntonH Lawtec
<unknown>"""
__docformat__ = 'plaintext'


import logging
from zExceptions import BadRequest
logger = logging.getLogger('collective.videolink: setuphandlers')
import os
from Products.CMFCore.utils import getToolByName
import transaction
from Products.ExternalMethod.ExternalMethod import manage_addExternalMethod
from Products.CMFCore.utils import getToolByName
from StringIO import StringIO
##code-section HEAD
##/code-section HEAD

PROFILE_ID = 'profile-collective.videolink:default'

def isNotcollectivevideolinkProfile(context):
    return context.readDataFile("collective.videolink_marker.txt") is None

def setupHideToolsFromNavigation(context):
    """hide tools"""
    if isNotcollectivevideolinkProfile(context): return 
    # uncatalog tools
    site = context.getSite()
    toolnames = ['portal_notifytool', 'portal_myccalendartool', 'portal_mycontractortool']
    portalProperties = getToolByName(site, 'portal_properties')
    navtreeProperties = getattr(portalProperties, 'navtree_properties')
    if navtreeProperties.hasProperty('idsNotToList'):
        for toolname in toolnames:
            try:
                portal[toolname].unindexObject()
            except:
                pass
            current = list(navtreeProperties.getProperty('idsNotToList') or [])
            if toolname not in current:
                current.append(toolname)
                kwargs = {'idsNotToList': current}
                navtreeProperties.manage_changeProperties(**kwargs)



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotcollectivevideolinkProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()

def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotcollectivevideolinkProfile(context): return
    #site = context.getSite()
    pass

    # enable folder creation for members
    #pm = site.portal_membership
    #pm.memberareaCreationFlag = True


def del_custom_client_report(context, logger=None):
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.videolink')

    urltool = getToolByName(context, "portal_url")
    portal  = urltool.getPortalObject()
    logger.info("deleting custom client_report")
    try:
        portal.portal_skins.custom.manage_delObjects(["client_report"])
        logger.info("custom client_report successfully deleted")
    except BadRequest:
        logger.info("no custom client_report found")
        
def add_workflow(context, logger=None):
    """Method to add new content type
       initially adds the reader type, but should work for 
       new types 
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.videolink')

    setup = getToolByName(context, 'portal_setup')
    logger.info("Looking for newly defined workflows and adding them")
    setup.runImportStepFromProfile(PROFILE_ID, 'workflow')
    logger.info("successfully updated workflows")
    logger.info("updating security (workflow role mappings)")
    wft = getToolByName(context, 'portal_workflow')
    wft.updateRoleMappings()

def add_type(context, logger=None):
    """Method to add new content type
       initially adds the reader type, but should work for 
       new types 
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.videolink')

    setup = getToolByName(context, 'portal_setup')
    logger.info("Looking for newly defined contenttypes and adding them")
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo')
    logger.info("Processed the type profile")

def add_role(context, logger=None):
    """Method to add new role
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.videolink')

    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'rolemap')
    logger.info("Looking for newly defined roles and adding them")


def add_catalog_indexes(context, logger=None):
    """Method to add our wanted indexes to the portal_catalog.

    @parameters:
    When called from the importVarious method below, 'context' is
    the plone site and 'logger' is the portal_setup logger.  But
    this method can also be used as upgrade step, in which case
    'context' will be portal_setup and 'logger' will be None.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.videolink')

    # Run the catalog.xml step as that may have defined new metadata
    # columns.  We could instead add <depends name="catalog"/> to
    # the registration of our import step in zcml, but doing it in
    # code makes this method usable as upgrade step as well.
    # Remove these lines when you have no catalog.xml file.
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'catalog')

    catalog = getToolByName(context, 'portal_catalog')
    indexes = catalog.indexes()
    # Specify the indexes you want, with ('index_name', 'index_type')
    wanted = (
              ('getLocation', 'FieldIndex'),
              ('thumbnail', 'FieldIndex'),
              )
    indexables = []
    for name, meta_type in wanted:
        if name not in indexes:
            catalog.addIndex(name, meta_type)
            indexables.append(name)
            logger.info("Added %s for field %s.", meta_type, name)
    if len(indexables) > 0:
        logger.info("Indexing new indexes %s.", ', '.join(indexables))
        catalog.manage_reindexIndex(ids=indexables)

def import_various(context):
    """Import step for configuration that is not handled in xml files.
    """
    # Only run step if a flag file is present
    if context.readDataFile('collective.videolink_marker.txt') is None:
        return
    logger = context.getLogger('collective.videolink')
    site = context.getSite()
    add_catalog_indexes(site, logger)

##code-section FOOT
##/code-section FOOT
