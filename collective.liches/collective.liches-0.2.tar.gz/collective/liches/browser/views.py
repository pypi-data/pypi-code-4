# -*- coding: utf-8 -*-
import hashlib
import logging
try:
    import simplejson as json
    from simplejson.decoder import JSONDecodeError
except ImportError:
    import json
    JSONDecodeError = ValueError
import time
import urllib, urllib2

from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage

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
        self.invalid_only = int(settings.invalid_only)

    def get_links(self):
        query = urllib.urlencode({"url": self.context.absolute_url(),
                "code": self.request.form.get('code', ''),
                "invalid": self.invalid_only,
                "format": "json"})
        if self.server_url.endswith('/'):
            service_url = "%sgetpages?%s" %(self.server_url, query)
        else:
            service_url = "%s/getpages?%s" %(self.server_url, query)
        try:
            data = json.load(urllib2.urlopen(service_url))
        except urllib2.HTTPError:
            return {'num': 'unknown', 'name': 'Error connecting to linkchecker server', 'urls': []}
        return data

class BrokenLinksView(BrowserView):

    template = ViewPageTemplateFile('brokenlinks.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILichesSettingsSchema)
        self.server_url = settings.liches_server
        self.invalid_only = settings.invalid_only
        url = urllib.urlencode({"url": self.context.absolute_url()})
        if self.server_url.endswith('/'):
            service_url = "%scheckurl?%s&format=json" %(self.server_url, url)
        else:
            service_url = "%s/checkurl?%s&format=json" %(self.server_url, url)
        try:
            self.data = json.load(urllib2.urlopen(service_url))
        except urllib2.HTTPError:
            self.data = {'num': 'unknown', 'name': 'Error connecting to linkchecker server', 'urls': []}


    def filter_invalid(self):
        if self.invalid_only:
            urls = []
            for url in self.data['urls']:
                if str(url['valid']).lower() == 'false':
                    urls.append(url)
                else:
                    continue
            return {'num': len(urls), 'name': self.data['name'], 'urls': urls}
        else:
            return self.data

    def get_broken_links(self):
        data = self.filter_invalid()
        return data

    def mark_broken_links(self):
        ready_template = """
        /*<![CDATA[*/
        $(document).ready(function() {
          %s
        });/*]]>*/ """
        mark_urls = []
        for url in self.filter_invalid()['urls']:
            mark_urls.append("""$("a[href='%s']").addClass('broken-link');""" % url['urlname'])
        return ready_template % ' '.join(mark_urls)

    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.template()

class LinkCheckPageView(BrowserView):

    secret_key = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ILichesSettingsSchema)
        self.secret_key = settings.secret_key
        self.server_url = settings.liches_server

    def __call__(self):
        url = self.context.absolute_url()
        t = str(int(time.time()/100))
        key = hashlib.md5(t + self.secret_key + url).hexdigest()
        query = urllib.urlencode({"url": url, "key": key})
        if self.server_url.endswith('/'):
            service_url = "%slinkcheckurl?%s&format=json" %(self.server_url, query)
        else:
            service_url = "%s/linkcheckurl?%s&format=json" % (self.server_url, query)
        try:
            data = json.load(urllib2.urlopen(service_url))
            logger.info(str(data))
            IStatusMessage(self.request).addStatusMessage(
                _(u"Link check started"), "info")
        except urllib2.HTTPError:
            IStatusMessage(self.request).addStatusMessage(
                _(u"Error communicating with Liches server"), "error")
        self.request.response.redirect(url)
        return u''

