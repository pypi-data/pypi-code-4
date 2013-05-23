# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.simple')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> _ = root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')
    >>> print http('GET /folder/++rest++testsimple HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 7
    Content-Type: plain/text
    <BLANKLINE>
    Nothing

  However we don't have PUT, POST, DELETE, HEAD actions:

    >>> print http('PUT /folder/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
       ...
    MethodNotAllowed: PUT

    >>> print http('POST /folder/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
       ...
    MethodNotAllowed: POST

    >>> print http('DELETE /folder/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
       ...
    MethodNotAllowed: DELETE

    >>> print http('DELETE /folder/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
       ...
    MethodNotAllowed: DELETE

    >>> print http('HEAD /folder/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
       ...
    MethodNotAllowed: HEAD

  If you test the view on a different object than a folder, it won't
  work as it is registered only for folders:

    >>> _ = root.manage_addProduct['OFS'].manage_addImage('image', 'Image')
    >>> print http('GET /image/++rest++testsimple HTTP/1.0')
    Traceback (most recent call last):
      ...
    NotFound: testsimple

"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import REST


class TestSimple(REST):
    grok.context(Folder)

    def GET(self):
        self.response.setHeader('Content-Type', 'plain/text')
        return "Nothing"
