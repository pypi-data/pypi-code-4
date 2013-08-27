# -*- coding: utf-8 -*-
# $Id: __init__.py 247099 2011-12-07 14:33:37Z vincentfretin $
"""aws.pdfbook component for Plone"""

import logging

from config import PROJECTNAME

logger = logging.getLogger(PROJECTNAME)
from zope.i18nmessageid import MessageFactory
translate = MessageFactory(PROJECTNAME)
