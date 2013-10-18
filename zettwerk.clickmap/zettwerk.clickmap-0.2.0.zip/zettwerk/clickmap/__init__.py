from zope.i18nmessageid import MessageFactory
clickmapMessageFactory = MessageFactory('zettwerk.clickmap')

import ClickmapTool

from Products.CMFCore import utils


def initialize(context):
    """Initializer called when used as a Zope 2 product."""

    utils.ToolInit('Zettwerk Clickmap', tools=(ClickmapTool.ClickmapTool,),
                   icon='z.png'
                   ).initialize(context)
