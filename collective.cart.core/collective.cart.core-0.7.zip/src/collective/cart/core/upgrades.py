from Products.CMFCore.utils import getToolByName

import logging


PROFILE_ID = 'profile-collective.cart.core:default'


def reimport_actions(context, logger=None):
    """Reimport actions"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting actions.')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions', run_dependencies=False, purge_old=False)


def reimport_rolemap(context, logger=None):
    """Reimport rolemap"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting rolemap.')
    setup.runImportStepFromProfile(PROFILE_ID, 'rolemap', run_dependencies=False, purge_old=False)


def reimport_typeinfo(context, logger=None):
    """Update typeinfo"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting typeinfo.')
    setup.runImportStepFromProfile(PROFILE_ID, 'typeinfo', run_dependencies=False, purge_old=False)


def reimport_workflows(context, logger=None):
    """Reimport workflows"""
    if logger is None:
        logger = logging.getLogger(__name__)
    setup = getToolByName(context, 'portal_setup')
    logger.info('Reimporting workflows.')
    setup.runImportStepFromProfile(
        PROFILE_ID, 'workflow', run_dependencies=False, purge_old=False)
    workflow = getToolByName(context, 'portal_workflow')
    workflow.updateRoleMappings()
