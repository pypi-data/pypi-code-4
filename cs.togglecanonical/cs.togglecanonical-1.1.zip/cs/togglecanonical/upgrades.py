from Products.CMFCore.utils import getToolByName

import logging

PROFILE_ID = 'profile-cs.togglecanonical:default'


def upgrade_to_1000(context, logger=None):

    if logger is None:
        # Called as upgrade step: define our own logger.
        logger = logging.getLogger('cs.togglecanonical')

    setup = getToolByName(context, 'portal_setup')
    setup.runImportStepFromProfile(PROFILE_ID, 'actions')
