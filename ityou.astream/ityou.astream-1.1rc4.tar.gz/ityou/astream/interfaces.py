#-*- coding: utf-8 -*-

from z3c.form import interfaces

from zope import schema
from zope.interface import Interface

from zope.i18nmessageid import MessageFactory

_ = MessageFactory('ityou.astream')

class IAstreamSettings(Interface):
    """Global activity stream settings. This describes records stored in the
    configuration registry and obtainable via plone.registry.
    """

    astream_delay = schema.Int(
            title=_(u"Time period for ajax requests"),
            description=_(u"Enter the time period between to Ajax-Requests. \
                    IMPORTANT: Be aware that time period less then 10 second may slow down your server! \
                    Time periods less then 4 seconds are not considered."),
            required=True,
            default=10,
        )


class IAstream(Interface):
    """Marker Interface
    """
    #allow_user_activities = schema.Bool(title=_(u"Status of user activities"),
    #                              description=_(u'help_user_activities',
    #                                            default=u"Should user be able to post activities to Activity Stream?"),
    #                              required=False,
    #                              default=False,)
    #
    #separate_streams = schema.Bool(title=_(u"Separate Streams"),
    #                              description=_(u'help_separate_streams',
    #                                            default=u"Should user activities appear in a separate stream?"),
    #                              required=False,
    #                              default=True,)

    #blacklist = schema.List(title=_(u"User Blacklist"),
    #                              description=_(u'help_user_blacklist',
    #                                            default=u"Of which users should no activities be generated?"),
    #                              required=False,
    #                              )

    