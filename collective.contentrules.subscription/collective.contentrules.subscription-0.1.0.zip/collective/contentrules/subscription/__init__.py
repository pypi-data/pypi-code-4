from zope.i18nmessageid import MessageFactory

subscriptionMessageFactory = MessageFactory(
    'collective.contentrules.subscription')

import logging
logger = logging.getLogger('collective.contentrules.subscription')

SUBSCRIPTION_TOOL = "contentrules_subscription_tool"


def initialize(context):
    """
    """
    # utils.ToolInit(SUBSCRIPTION_TOOL,
    #                tools=(Tool,),
    #                product_name=SUBSCRIPTION_TOOL,
    #                icon='browser/tool.png',
    #                ).initialize(context)
