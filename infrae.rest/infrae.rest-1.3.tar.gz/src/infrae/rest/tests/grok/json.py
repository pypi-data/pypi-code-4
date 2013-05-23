# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.json')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')

    >>> print http('GET /folder/++rest++testjson HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 32
    Content-Type: application/json
    <BLANKLINE>
    {"integer": 42, "boolean": true}

  You can optionaly provide values:

    >>> print http('PUT /folder/++rest++testjson HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 20
    Content-Type: application/json
    <BLANKLINE>
    {"identifier": null}

    >>> print http('PUT /folder/++rest++testjson HTTP/1.0\\r\\n'
    ...     'Content-Length: 13\\r\\n'
    ...     'Content-Type: application/x-www-form-urlencoded\\r\\n\\r\\n'
    ...     'identifier=42')
    HTTP/1.0 200 OK
    Content-Length: 20
    Content-Type: application/json
    <BLANKLINE>
    {"identifier": "42"}

    >>> print http('HEAD /folder/++rest++testjson HTTP/1.0')
    HTTP/1.0 204 No Content
    <BLANKLINE>
    <BLANKLINE>

"""

from OFS.Folder import Folder
from five import grok
from infrae.rest import REST


class TestJSon(REST):
    grok.context(Folder)

    def GET(self):
        return self.json_response({'boolean': True, 'integer': 42})

    def PUT(self, identifier=None):
        return self.json_response({'identifier': identifier})

    def HEAD(self):
        return None

