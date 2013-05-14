# -*- coding: utf-8 -*-
"""Define a portlet used to show grouplist. This follows the patterns from
plone.app.portlets.portlets. Note that we also need a portlet.xml in the
GenericSetup extension profile to tell Plone about our new portlet.
"""

import random

from Acquisition import aq_inner

from zope import schema
from zope.formlib import form
from zope.interface import implements
from zope.component import getMultiAdapter

from plone.app.portlets.portlets import base
from plone.memoize.instance import memoize
from plone.portlets.interfaces import IPortletDataProvider

from DateTime import DateTime
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from ityou.whoisonline import _

from .utils import WhoAmIUtils

class IWhoAmIPortlet(IPortletDataProvider):

    show_all = schema.Bool(
            title=_(u"Display all profile data"),
            description=_(u"All profile data will be displayed"),
            required=True,
            default=True,
        )

class Assignment(base.Assignment):
    implements(IWhoAmIPortlet)

    def __init__(self, show_all=True):
        self.show_all = show_all

    title = _(u"WhoAmI")

class Renderer(base.Renderer):

    _template = ViewPageTemplateFile('whoami.pt')
    
    def render(self):

        context = aq_inner(self.context)
        mt = getToolByName(context, 'portal_membership')
        
        if not mt.isAnonymousUser():
            return self._template()
               
    @property
    def available(self):
        return True

    def user_profile(self):
        """Show profile of the actual user
        """
        context = aq_inner(self.context)
        # extern utils; no need to restart zope on changes
        who = WhoAmIUtils()
                       
        return who.user_profile(context, self.data.show_all)

class AddForm(base.AddForm):
    form_fields = form.Fields(IWhoAmIPortlet)
    label = _(u"Add WhoAmI portlet")
    description = _(u"This portlet displays online users.")

    def create(self, data):
        assignment = Assignment()
        form.applyChanges(assignment, self.form_fields, data)
        return assignment

class EditForm(base.EditForm):
    form_fields = form.Fields(IWhoAmIPortlet)
    label = _(u"Edit WhoAmI portlet")
    description = _(u"This portlet displays online users.")
    
