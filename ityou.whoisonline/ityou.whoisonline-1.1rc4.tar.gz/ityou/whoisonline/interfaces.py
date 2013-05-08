#-*- coding: utf-8 -*-

from z3c.form import interfaces

from zope import schema
from zope.interface import Interface

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('ityou.whoisonline')

class IWhoIsOnlineSettings(Interface):
    """Global whoisonline settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """
    timeout_online = schema.Int(
            title=_(u"Online timeout"),
            description=_(u"For how long should a user be marked as online? (Seconds) "),
            required=True,
            default=600,
        )
    max_users = schema.Int(
            title=_(u"Maximal number of users"),
            description=_(u"The maximum number of user that should be listed in the 'who is online'-portlet"),
            required=True,
            default=20,
        )

    whoisonline_delay = schema.Int(
            title=_(u"Time period for ajax requests"),
            description=_(u"Enter the time period between to Ajax-Requests. \
                    IMPORTANT: Be aware that time period less then 10 second may slow down your server! \
                    Time periods less then 4 seconds are not considered."),
            required=True,
            default=10,
        )
    
class IWhoIsOnline(Interface):
    """Marker interface
    """
