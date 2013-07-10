# -*- coding: utf-8 -*-

import logging
from zope.i18nmessageid import MessageFactory

custommenuMessageFactory = MessageFactory('redturtle.custommenu.factories')
logger = logging.getLogger('redturtle.custommenu.factories')

def initialize(context):
    """Initializer called when used as a Zope 2 product."""
