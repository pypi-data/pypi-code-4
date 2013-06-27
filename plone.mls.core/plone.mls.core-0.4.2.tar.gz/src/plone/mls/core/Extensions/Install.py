# -*- coding: utf-8 -*-
"""Install/Uninstall methods."""

# python imports
from logging import getLogger

# zope imports
from Products.CMFCore.utils import getToolByName


UNINSTALL_PROFILE = 'profile-plone.mls.core:uninstall'
logger = getLogger('plone.mls.core')


def uninstall(portal):
    portal_setup = getToolByName(portal, 'portal_setup')
    portal_setup.runAllImportStepsFromProfile(UNINSTALL_PROFILE)
    logger.info('Ran all uninstall steps.')
