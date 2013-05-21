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
# FOR A PARTICULAR PURPOSE
#
##############################################################################
"""Test Zopache Page Template Evaluation
"""
from unittest import TestCase, main, makeSuite
from zope.testing.cleanup import CleanUp # Base class w registry cleanup
from zope.container.contained import contained
from zopache.pagetemplate.browser.pagetemplate import ZopachePageTemplateEval

class Test(CleanUp, TestCase):

    def testTemplateRendering(self):

        class Template(object):
            def render(self, request, **kw):
                self.called = request, kw
                return 42

            content_type = 'text/x-test'

        class Folder(object):
            name='zope'
        folder = Folder()

        class Response(object):

            base = None

            def setBase(self, base):
                self.base = base

            def setHeader(self, name, value):
                setattr(self, name, value)

        class Request(object):

            response = Response()

            URL = ['http://localhost', 'http://localhost/pt']

        request = Request()
        template = contained(Template(), folder)

        view = ZopachePageTemplateEval()
        # Do manually, since directive adds BrowserView as base class
        view.context = template
        view.request = request
        self.assertEqual(view.index(), 42)
        self.assertEqual(template.called, (request, {}))
        self.assertEqual(getattr(request.response, 'content-type'),
                         'text/x-test')

def test_suite():
    return makeSuite(Test)
