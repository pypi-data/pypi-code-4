# -*- coding: utf-8 -*-
import random
from Acquisition import aq_inner

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter
from zope.component import getUtility

from zope.app.component.hooks import getSite
from plone.registry.interfaces import IRegistry

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from .. import _
from ..interfaces import IWhoIsOnlineSettings
from .utils import WhoIsOnlineUtils
from ..config import MIN_WHOISONLINE_DELAY

class IWhoIsOnlinePortlet(IPortletDataProvider):

    count = schema.Int(
            title=_(u"Number of online users to display"),
            description=_(u"Maximum number of online users to show"),
            required=True,
            default=20,
        )

class Assignment(base.Assignment):
    implements(IWhoIsOnlinePortlet)

    def __init__(self, count=20):
        self.count = count

    title = _(u"Who Is Online")

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('whoisonline.pt')
    
    def render(self):
        
        context = aq_inner(self.context)
        mt = getToolByName(context, 'portal_membership')
        
        ru =  getUtility(IRegistry)
        # *1000: transform milliseconds to seconds
        # We put this value in the Portlet DOM so that
        # jquery can fetch it
        # if value lower than MIN_WHOISONLINE_DELAY,
        # we take MIN_WHOISONLINE_DELAY
        self.WHOISONLINE_DELAY = max([ru.forInterface(IWhoIsOnlineSettings).whoisonline_delay*1000, MIN_WHOISONLINE_DELAY])
        self.ESI_ROOT = getSite().absolute_url()
        # only show if not Anonymous    
        if not mt.isAnonymousUser():
            return self._template()
       
    @property
    def available(self):
        #return len(XXX) > 0
        return True

    def who_is_online_list(self):
        """Show online users
        """
        # extern utils; no need to restart zope on changes
        who = WhoIsOnlineUtils()
        limit = self.data.count
        return who.who_is_online_list()[:limit]

class AddForm(base.AddForm):
    form_fields = form.Fields(IWhoIsOnlinePortlet)
    label = _(u"Add WhoIsOnline portlet")
    description = _(u"This portlet displays online users.")

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(IWhoIsOnlinePortlet)
    label = _(u"Edit WhoIsOnline portlet")
    description = _(u"This portlet displays online users.")
    
