# -*- coding: utf-8 -*-

from zope.interface import implements

from plone.memoize import ram

from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from cciaa.portlet.calendar import PortletCalendarioCameraleMessageFactory as _

from plone.app.portlets.portlets.calendar import ICalendarPortlet
from plone.app.portlets.portlets.calendar import Assignment as CameraleAssignment
from plone.app.portlets.portlets.calendar import Renderer as CameraleRenderer
from plone.app.portlets.portlets.calendar import AddForm as CameraleAddForm
from plone.app.portlets.portlets.calendar import _render_cachekey

from plone.memoize.compress import xhtml_compress

class IPortletCalendarioCamerale(ICalendarPortlet):
    """A portlet displaying a calendar
    """

class Assignment(CameraleAssignment):

    implements(IPortletCalendarioCamerale)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Searching Calendar")

class Renderer(CameraleRenderer):
    _template = ViewPageTemplateFile('portletcalendariocamerale.pt')
    updated = False

    def __init__(self, context, request, view, manager, data):
        CameraleRenderer.__init__(self, context, request, view, manager, data)

    @ram.cache(_render_cachekey)
    def render(self):
        return xhtml_compress(self._template())
    
    def dateStart(self,month,year):
        dateS=str(year)+"-"+str(month)+"-1"
        return dateS

    def dateEnd(self,month,year):
        if month==12:
            dateE=str(year+1)+"-1-1"
        else:
            dateE=str(year)+"-"+str(month+1)+"-1"
        return dateE

class AddForm(CameraleAddForm):
    form_fields = form.Fields(IPortletCalendarioCamerale)

    def create(self):
        return Assignment()
