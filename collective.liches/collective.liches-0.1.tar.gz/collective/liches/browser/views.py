# -*- coding: utf-8 -*-
import urllib, urllib2
import logging
try:
    import simplejson as json
    from simplejson.decoder import JSONDecodeError
except ImportError:
    import json
    JSONDecodeError = ValueError

from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry

from collective.liches import lichesMessageFactory as _
from collective.liches.interfaces import ILichesSettingsSchema

logger = logging.getLogger('collective.liches')

class IStartPageView(Interface):
    """
    Public view interface
    """



class StartPageView(BrowserView):
    """
    Public browser view
    """
    implements(IStartPageView)
    template = ViewPageTemplateFile('startp.pt')
    content_types=['Document']

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILichesSettingsSchema)
        self.content_types = settings.content_types

    @property
    def portal_catalog(self):
        return getToolByName(self.context, 'portal_catalog')

    @property
    def portal(self):
        return getToolByName(self.context, 'portal_url').getPortalObject()

    def get_links(self):
        brains = self.portal_catalog(portal_type=self.content_types)
        return brains

    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.template()

class IBrokenPagesView(Interface):
    """ Marker nterface """

class BrokenPagesView(BrowserView):
    implements(IBrokenPagesView)
    server_url = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILichesSettingsSchema)
        self.server_url = settings.liches_server

    def get_links(self):
        url = urllib.urlencode({"url": self.context.absolute_url()})
        if self.server_url.endswith('/'):
            service_url = "%sgetpages?%s&format=json" %(self.server_url, url)
        else:
            service_url = "%s/getpages?%s&format=json" %(self.server_url, url)
        try:
            data = json.load(urllib2.urlopen(service_url))
        except urllib2.HTTPError:
            return {'num': 'unknown', 'name': 'Error connecting to linkchecker server', 'urls': []}
        return data

class BrokenLinksView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILichesSettingsSchema)
        self.server_url = settings.liches_server
        url = urllib.urlencode({"url": self.context.absolute_url()})
        if self.server_url.endswith('/'):
            service_url = "%scheckurl?%s&format=json" %(self.server_url, url)
        else:
            service_url = "%s/checkurl?%s&format=json" %(self.server_url, url)
        try:
            self.data = json.load(urllib2.urlopen(service_url))
        except urllib2.HTTPError:
            self.data = {'num': 'unknown', 'name': 'Error connecting to linkchecker server', 'urls': []}

    def get_broken_links(self):
        return self.data

    def mark_broken_links(self):
        ready_template = """
        /*<![CDATA[*/
        $(document).ready(function() {
          %s
        });/*]]>*/ """
        mark_urls = []
        for url in self.data['urls']:
            mark_urls.append("""$("a[href='%s']").addClass('broken-link');""" % url['urlname'])
        return ready_template % ' '.join(mark_urls)
