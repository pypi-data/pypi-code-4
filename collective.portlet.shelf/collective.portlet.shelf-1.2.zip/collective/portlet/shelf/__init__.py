from zope.i18nmessageid import MessageFactory
PortletShelfMessageFactory = MessageFactory('collective.portlet.shelf')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
