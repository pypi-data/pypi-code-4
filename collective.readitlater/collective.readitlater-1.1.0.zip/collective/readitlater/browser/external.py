from plone.z3cform import z2
from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from z3c.form.interfaces import IFormLayer
from zope.component import getMultiAdapter


class ShowAll(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        path = portal_state.navigation_root_url()
        self.url = '%s/@@collective_readitlater_script' % path
        self.script = "javascript:void((function(){"
        self.script += "var%20hsb=document.createElement('script');"
        self.script += "hsb.setAttribute('src','%s');" % self.url
        self.script += "hsb.setAttribute('type','text/javascript');"
        self.script += "document.getElementsByTagName('head')[0].appendChild(hsb);"
        self.script += "})());"
        return self.index()


class Script(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        context = self.context.aq_inner
        portal_state = getMultiAdapter((context, self.request),
                                      name=u'plone_portal_state')
        path = portal_state.navigation_root_url()
        self.url_iframe = '%s/@@collective_readitlater_iframe' % path
        self.url_css = '%s/@@collective_readitlater_style' % path
        self.request.response.setHeader('Content-Type',
                                        'text/javascript')
        return self.index()


class Style(BrowserView):
    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.request.response.setHeader('Content-Type',
                                        'text/css')
        return self.index()
