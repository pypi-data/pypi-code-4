# -*- coding: utf-8 -*-
import logging
from Products.CMFCore.utils import getToolByName

# The profile id of your package:
PROFILE_ID = 'profile-collective.liches:default'


def upgrade_registry(context, logger=None):
    """Re-import the portal configuration registry settings.
    """
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.liches')
    logger.info("Update registry")
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'plone.app.registry')
    return

def add_portlet(context, logger=None):
    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('collective.liches')
    logger.info("register portlets")
    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'portlets')
    return
