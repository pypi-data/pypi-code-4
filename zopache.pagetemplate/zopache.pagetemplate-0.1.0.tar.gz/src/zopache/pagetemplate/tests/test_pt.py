##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
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
"""Basic tests for Page Templates used in content-space.
"""
import unittest

from zope.component import getMultiAdapter, provideAdapter
from zope.interface import directlyProvides, Interface
from zope.interface.verify import verifyClass
from zope.security.interfaces import Forbidden
from zope.security.checker import NamesChecker, defineChecker
from zope.publisher.browser import TestRequest, BrowserView
from zope.location.traversing import LocationPhysicallyLocatable
from zope.traversing.adapters import Traverser, DefaultTraversable
from zope.traversing.adapters import RootPhysicallyLocatable
from zope.traversing.interfaces import ITraverser, ITraversable
from zope.traversing.interfaces import IPhysicallyLocatable
from zope.traversing.interfaces import IContainmentRoot

from zope.app.testing.placelesssetup import PlacelessSetup
from zope.container.contained import contained

from zopache.pagetemplate.interfaces import IZopachePageTemplate
from zopache.pagetemplate.pagetemplate import ZopachePageTemplate, Sized


class Data(object):
    def __init__(self, **kw):
        self.__dict__.update(kw)


class ZopachePageTemplateTests(PlacelessSetup, unittest.TestCase):

    def setUp(self):
        super(ZopachePageTemplateTests, self).setUp()
        provideAdapter(Traverser, (None,), ITraverser)
        provideAdapter(DefaultTraversable, (None,), ITraversable)
        provideAdapter(
              LocationPhysicallyLocatable, (None,), IPhysicallyLocatable)
        provideAdapter(
              RootPhysicallyLocatable, (IContainmentRoot,), IPhysicallyLocatable)
        defineChecker(Data, NamesChecker(['URL', 'name']))

    def testZPTRendering(self):
        page = ZopachePageTemplate()
        page.setSource(
            u''
            '<html>'
            '<head><title tal:content="options/title">blah</title></head>'
            '<body>'
            '<a href="foo" tal:attributes="href request/URL/1">'
            '<span tal:replace="container/name">splat</span>'
            '</a></body></html>'
            )

        page = contained(page, Data(name='zope'))

        request = Data(URL={'1': 'http://foo.com/'},
                       debug=Data(showTAL=False, sourceAnnotations=False))
        out = page.render(request, title="Zope rules")
        out = ' '.join(out.split())

        self.assertEqual(
            out,
            '<html><head><title>Zope rules</title></head><body>'
            '<a href="http://foo.com/">'
            'zope'
            '</a></body></html>'
            )

    def test_request_protected(self):
        page = ZopachePageTemplate()
        page.setSource(
            u'<p tal:content="python: request.__dict__" />'
            )

        page = contained(page, Data(name='zope'))

        request = Data(debug=Data(showTAL=False, sourceAnnotations=False))
        self.assertRaises(Forbidden, page.render, request)

    def test_template_context_wrapping(self):

        class AU(BrowserView):
            def __str__(self):
                name = self.context.__name__
                if name is None:
                    return 'None'
                return name

        defineChecker(AU, NamesChecker(['__str__']))

        from zope.traversing.namespace import view
        from zope.traversing.interfaces import ITraversable
        provideAdapter(view, (None,), ITraversable, name="view")
        provideAdapter(view, (None, None), ITraversable, name="view")
        provideAdapter(
            AU, (IZopachePageTemplate, TestRequest), Interface, name='name')

        page = ZopachePageTemplate()
        page.setSource(
            u'<p tal:replace="template/@@name" />'
            )
        page = contained(page, None, name='zpt')
        request = TestRequest()
        self.assertEquals(page.render(request), u'zpt')

    def test_source_file(self):
        page = ZopachePageTemplate()
        self.assert_(page.pt_source_file() is None)

        page = self.pageInContext(page)
        self.assertEquals(page.pt_source_file(), '/folder/zpt')

    def pageInContext(self, page):
        root = Data()
        directlyProvides(root, IContainmentRoot)
        folder = contained(Data(), root, name='folder')
        return contained(page, folder, name='zpt')

    def test_debug_flags(self):
        page = ZopachePageTemplate()
        page = self.pageInContext(page)
        page.setSource(u'<tal:x>Foo</tal:x>')

        request = TestRequest()
        self.assertEquals(page.render(request), u'Foo')

        request.debug.showTAL = True
        self.assertEquals(page.render(request), u'<tal:x>Foo</tal:x>')

        request.debug.showTAL = False
        request.debug.sourceAnnotations = True
        self.assertEquals(page.pt_source_file(), '/folder/zpt')
        self.assertEquals(page.render(request),
            '<!--\n' +
            '=' * 78 + '\n' +
            '/folder/zpt (line 1)\n' +
            '=' * 78 + '\n' +
            '-->Foo')


class DummyZPT(object):

    def __init__(self, source):
        self.source = source

    def getSource(self):
        return self.source

class SizedTests(unittest.TestCase):

    def testInterface(self):
        from zope.size.interfaces import ISized
        self.failUnless(ISized.implementedBy(Sized))
        self.failUnless(verifyClass(ISized, Sized))

    def test_zeroSized(self):
        s = Sized(DummyZPT(''))
        self.assertEqual(s.sizeForSorting(), ('line', 0))
        self.assertEqual(s.sizeForDisplay(), u'0 lines')

    def test_oneSized(self):
        s = Sized(DummyZPT('one line'))
        self.assertEqual(s.sizeForSorting(), ('line', 1))
        self.assertEqual(s.sizeForDisplay(), u'1 line')

    def test_arbitrarySize(self):
        s = Sized(DummyZPT('some line\n'*5))
        self.assertEqual(s.sizeForSorting(), ('line', 5))
        self.assertEqual(s.sizeForDisplay(), u'5 lines')


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(ZopachePageTemplateTests),
        unittest.makeSuite(SizedTests),
        ))

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
