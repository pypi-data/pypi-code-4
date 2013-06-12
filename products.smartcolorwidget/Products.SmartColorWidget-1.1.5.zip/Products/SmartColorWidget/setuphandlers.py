# -*- coding: utf-8 -*-
# $Id: setuphandlers.py 9248 2009-11-11 09:51:09Z glenfant $
"""Additional installation manual steps"""

import logging
LOG = logging.getLogger('SmartColorWidget')

from Products.Archetypes.public import listTypes
from Products.Archetypes.Extensions.utils import installTypes
from Products.SmartColorWidget.config import *

def importFinalSteps(context):
    """Final settings
    """
    marker = context.readDataFile('smartcolorwidget.txt')
    if marker is None:
        return

    site = context.getSite()
    setupDemoTypes(site)

def setupDemoTypes(context):
    """
    install demo types if required by config
    """

    classes = listTypes(PROJECTNAME)
    if INSTALL_DEMO_TYPES:
        installTypes(context, out, classes, PROJECTNAME)
    LOG.info("Demo types successfully installed for %s." % PROJECTNAME)
