# -*- coding: utf-8 -*-

from Products.SmartColorWidget import LOG

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.runAllImportStepsFromProfile('profile-Products.SmartColorWidget:uninstall')
        LOG.info("SmartColorWidget removed")