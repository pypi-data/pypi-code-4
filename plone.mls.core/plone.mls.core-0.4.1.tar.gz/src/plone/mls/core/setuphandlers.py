# -*- coding: utf-8 -*-
"""Additional setup steps."""

# python imports
from logging import getLogger

# zope imports
from plone.browserlayer import utils as layerutils

# local imports
from plone.mls.core.browser.interfaces import IMLSSpecific

logger = getLogger('plone.mls.core')


def resetLayers(context):
    """Remove custom browser layer on uninstall."""

    if context.readDataFile('plone.mls.core_uninstall.txt') is None:
        return

    if IMLSSpecific in layerutils.registered_layers():
        layerutils.unregister_layer(name='plone.mls.core')
        logger.info('Browser layer "plone.mls.core" uninstalled.')
