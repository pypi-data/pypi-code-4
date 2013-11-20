# -*- coding: utf-8 -*-
import os
import logging

from plone.resource.interfaces import IResourceDirectory
from zope.component import queryUtility
from zope.i18nmessageid import MessageFactory

from stxnext.grayscale.config import TYPE, THEME

log = logging.getLogger('stxnext.grayscale')
StxnextGrayscaleMessageFactory = MessageFactory('stxnext.grayscale')


def initialize(context):
    """
    Initializer called when used as a Zope 2 product.
    """
    resource_dir = queryUtility(IResourceDirectory, name=u'')
    if resource_dir:
        if not TYPE in resource_dir.listDirectory():
            path = os.path.join(resource_dir.directory, TYPE)
            os.makedirs(os.path.normpath(path))
            log.info("Created directory for stroring grayscaled resources: %s" % path)
        grayscale_dir = resource_dir[TYPE]
        if not THEME in grayscale_dir.listDirectory():
            path = os.path.join(grayscale_dir.directory, THEME)
            os.makedirs(os.path.normpath(path))
            log.info("Created directory for stroring grayscaled resources: %s" % path)
