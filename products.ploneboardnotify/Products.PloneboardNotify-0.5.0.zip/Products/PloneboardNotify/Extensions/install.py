# -*- coding: utf-8 -*-

from Products.PloneboardNotify import logger

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-Products.PloneboardNotify:uninstall')
        # manually deleting properties sheet
        portal.portal_properties.manage_delObjects(['ploneboard_notify_properties'])
        logger.info("Deleted ploneboard_notify_properties property sheet")
        logger.info("Uninstallation done")
