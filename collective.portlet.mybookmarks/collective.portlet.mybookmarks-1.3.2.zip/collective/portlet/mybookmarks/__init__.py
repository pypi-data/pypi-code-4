from zope.i18nmessageid import MessageFactory
MyBookmarksPortletMessageFactory = MessageFactory('collective.portlet.mybookmarks')
import logging
logger = logging.getLogger('collective.portlet.mybookmarks')


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
