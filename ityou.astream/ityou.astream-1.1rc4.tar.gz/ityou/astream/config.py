# -*- coding: utf-8 -*-
from . import _
from zope.component import getUtility
from plone.registry.interfaces import IRegistry

DEBUG       = False

ACTIVITY_STREAM = '@@activity-stream'
USER_ID_BLACKLIST = ['admin']
MESSAGE_TEXT_CONTAINER = {
    'title':        _(u'has edited the title of <i>${name}</i>.'),
    'description':  _(u'has edited the description of <i>${name}s</i>.'),
    'text':         _(u'has edited the content of <i>${name}</i>.'),
    'create':       _(u'has created <i>${name}</i>.'),
    'copy':         _(u'has copied <i>${name}</i>.'),
    'undefined':    _(u'has edited/created <i>${name}</i>.'),
    'edit':         _(u'has edited <i>${name}</i>.')
}                   
TIME_STRING = u"%d.%m.%Y - %H:%M"
MIN_ASTREAM_DELAY = 4000
