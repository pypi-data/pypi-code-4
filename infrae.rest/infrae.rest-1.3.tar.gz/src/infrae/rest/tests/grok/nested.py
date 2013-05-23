# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

   Grok the test first:

   >>> grok('infrae.rest.tests.grok.nested')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> _ = root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')
    >>> print http('GET /folder/++rest++testroot HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 4
    Content-Type: plain/text
    <BLANKLINE>
    Root

  We can access sub-handlers, but only going through the root handler:

    >>> print http('GET /folder/++rest++testroot/testchildfirst HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 11
    Content-Type: plain/text
    <BLANKLINE>
    Child First

    >>> print http('GET /folder/++rest++testchildfirst HTTP/1.0')
    Traceback (most recent call last):
       ...
    NotFound: testchildfirst

  And sub-handlers can have themselves sub-handlers:

    >>> print http('GET /folder/++rest++testroot/testchildfirst/testgrandchildfirst HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 17
    Content-Type: plain/text
    <BLANKLINE>
    Grand Child First

  Same way, sub-handlers can have security and a specific name:

    >>> print http('GET /folder/++rest++testroot/otherchild HTTP/1.0')
    HTTP/1.0 401 Unauthorized
    Content-Length: 0
    Www-Authenticate: basic realm="Zope"
    <BLANKLINE>
    <BLANKLINE>

"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import REST


class TestRoot(REST):
    grok.context(Folder)

    def GET(self):
        self.response.setHeader('Content-Type', 'plain/text')
        return "Root"


class TestChildFirst(REST):
    grok.adapts(TestRoot, Folder)

    def GET(self):
        self.response.setHeader('Content-Type', 'plain/text')
        return "Child First"


class TestChildSecond(REST):
    grok.adapts(TestRoot, Folder)
    grok.name('otherchild')
    grok.require('zope2.ViewManagementScreens')

    def GET(self):
        self.response.setHeader('Content-Type', 'plain/text')
        return "Child Second"


class TestGrandChildFirst(REST):
    grok.adapts(TestChildFirst, Folder)

    def GET(self):
        self.response.setHeader('Content-Type', 'plain/text')
        return "Grand Child First"
