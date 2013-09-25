# -*- coding: utf-8 -*-
from plone import api

from collective.local.sentmail import _


def isNotCurrentProfile(context):
    return context.readDataFile("collectivelocalsentmail_marker.txt") is None


def post_install(context):
    """Post install script"""
    if isNotCurrentProfile(context): return
    portal = context.getSite()
    if "sent-mails" not in portal:
        mails_folder = api.content.create(type="sent_mails_folder",
                                          title=_(u"Sent mails"),
                                          container=portal)
