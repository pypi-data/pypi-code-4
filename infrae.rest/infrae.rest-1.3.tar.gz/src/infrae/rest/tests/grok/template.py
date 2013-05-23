# -*- coding: utf-8 -*-
# Copyright (c) 2012-2013 Infrae. All rights reserved.
# See also LICENSE.txt
"""

  Let's first grok our test first:

   >>> grok('infrae.rest.tests.grok.template_fixture')

  Now, if we have a folder we can use our REST component:

    >>> root = getRootFolder()
    >>> root.manage_addProduct['OFS'].manage_addFolder('folder', 'Folder')
    >>> from five.localsitemanager import make_site
    >>> make_site(root.folder)

  We can now fetch the component with the template:

    >>> print http('GET /folder/++rest++form HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 168
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    <form>
       <h1>42</h1>
      <link rel="stylesheet" type="text/css"
            href="http://localhost/folder/@@/infrae.rest.tests.grok.template_fixture/style.css" />
    </form>
    <BLANKLINE>

  And the nested one as well:

    >>> print http('GET /folder/++rest++form/widget HTTP/1.0')
    HTTP/1.0 200 OK
    Content-Length: 15
    Content-Type: text/html;charset=utf-8
    <BLANKLINE>
    <span>51</span>


"""
