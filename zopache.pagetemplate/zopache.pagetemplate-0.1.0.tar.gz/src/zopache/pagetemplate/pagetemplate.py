##############################################################################
#
# Copyright (c) 2013 Christopher Lozinski (lozinski@freerecruiting.com).
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""TTW PageTemplate
"""
from persistent import Persistent

from zope.security.proxy import ProxyFactory
from zope.interface import implements
from zope.pagetemplate.pagetemplate import PageTemplate
from zope.size.interfaces import ISized
from zope.publisher.browser import BrowserView
from zope.traversing.api import getPath

from zope.pagetemplate.engine import AppPT
from zope.container.contained import Contained
from zope.app.publication.interfaces import IFileContent

from zopache.pagetemplate.interfaces import \
    IZopachePageTemplate, IRenderZopachePageTemplate


class ZopachePageTemplate(AppPT, PageTemplate, Persistent, Contained):
    implements(IZopachePageTemplate, IRenderZopachePageTemplate, IFileContent)
    expand = False
    evaluateInlineCode = False

    def getSource(self, request=None):
        return self.read(request)

    def setSource(self, text, content_type='text/html'):
        if not isinstance(text, unicode):
            raise TypeError("source text must be Unicode" , text)
        self.pt_edit(text, content_type)

    source = property(getSource, setSource)

    def pt_getEngineContext(self, namespace):
        context = self.pt_getEngine().getContext(namespace)
        context.evaluateInlineCode = self.evaluateInlineCode
        return context

    def pt_getContext(self, instance, request, **_kw):
        # instance is a View component
        namespace = super(ZopachePageTemplate, self).pt_getContext(**_kw)
        namespace['template'] = self
        namespace['request'] = request
        namespace['container'] = namespace['context'] = instance
        return namespace

    def pt_source_file(self):
        try:
            return getPath(self)
        except TypeError:
            return None

    def render(self, request, *args, **keywords):
        instance = self.__parent__

        debug_flags = request.debug
        request = ProxyFactory(request)
        instance = ProxyFactory(instance)
        if args:
            args = ProxyFactory(args)
        kw = ProxyFactory(keywords)

        namespace = self.pt_getContext(instance, request,
                                       args=args, options=kw)

        return self.pt_render(namespace, showtal=debug_flags.showTAL,
                              sourceAnnotations=debug_flags.sourceAnnotations)


class Sized(object):

    implements(ISized)

    def __init__(self, page):
        self.num_lines = len(page.getSource().splitlines())

    def sizeForSorting(self):
        'See ISized'
        return ('line', self.num_lines)

    def sizeForDisplay(self):
        'See ISized'
        if self.num_lines == 1:
            return u'1 line'
        return u'%s lines' % str(self.num_lines)
