# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.require')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')

  And try to access it like this:

    >>> print http('GET /folder/++rest++secret HTTP/1.0')
    HTTP/1.0 401 Unauthorized
    Content-Length: 0
    Www-Authenticate: basic realm="Zope"
    <BLANKLINE>

  Ok if we authenticate ourselves it will work:

    >>> print http('GET /folder/++rest++secret HTTP/1.0\\r\\n'
    ...      'Authorization: Basic manager:manager')
    HTTP/1.0 200 OK
    Content-Length: 13
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    <p>Secret</p>

"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import REST


class TestSecret(REST):
    grok.context(Folder)
    grok.name('secret')
    grok.require('zope2.ViewManagementScreens')

    def GET(self):
        return "<p>Secret</p>"
