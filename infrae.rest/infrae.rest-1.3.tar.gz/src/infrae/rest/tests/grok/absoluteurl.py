# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.absoluteurl')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')

  If we access it, it should return its URL:

    >>> print http('GET /folder/++rest++url HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 35
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    http://localhost/folder/++rest++url

  That also works for nest components:

    >>> print http('GET /folder/++rest++url/nested1 HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 43
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    http://localhost/folder/++rest++url/nested1

    >>> print http('GET /folder/++rest++url/nested2 HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 43
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    http://localhost/folder/++rest++url/nested2


"""
from OFS.Folder import Folder
from five import grok
from infrae.rest import REST
from zope.traversing.browser import absoluteURL


class URLTest(REST):
    grok.context(Folder)
    grok.name('url')

    def GET(self):
        return absoluteURL(self, self.request)


class Nested1URLTest(REST):
    grok.adapts(URLTest, Folder)
    grok.name('nested1')

    def GET(self):
        return absoluteURL(self, self.request)


class Nested2URLTest(REST):
    grok.adapts(URLTest, Folder)
    grok.name('nested2')

    def GET(self):
        return absoluteURL(self, self.request)

