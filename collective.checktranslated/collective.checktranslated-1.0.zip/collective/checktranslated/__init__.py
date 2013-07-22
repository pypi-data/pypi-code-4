# -*- extra stuff goes here -*-

from zope.i18nmessageid import MessageFactory
checktranslatedMessageFactory = MessageFactory('collective.checktranslated')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
