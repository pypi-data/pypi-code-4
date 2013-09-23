# -*- coding: utf-8 -*-
"""Init and utils."""
from logging import getLogger
from zope.i18nmessageid import MessageFactory

PROJECTNAME = 'redturtle.gritterize'

gritterizeMessageFactory = MessageFactory(PROJECTNAME)
gritterizeLogger = getLogger(PROJECTNAME)


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
