# -*- coding: utf-8 -*-
# $Id: utils.py 246996 2011-12-04 19:08:08Z vincentfretin $
"""Misc utilities"""

from Products.Five.browser import BrowserView
from zope.component import queryMultiAdapter
from Products.CMFCore.utils import getToolByName

from aws.pdfbook.interfaces import IPDFOptions

class PDFBookEnabled(BrowserView):

    def __call__(self):
        if 'portal_factory' in self.request.URL:
            return False

        context = self.context
        transformer = queryMultiAdapter((context, self.request), name=u'printlayout')
        portal = getToolByName(context, 'portal_url').getPortalObject()
        options = IPDFOptions(portal)
        return bool(transformer) and (context.portal_type not in options.disallowed_types)
