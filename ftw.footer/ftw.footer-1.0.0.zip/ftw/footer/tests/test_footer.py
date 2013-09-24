from ftw.builder import Builder
from ftw.builder import create
from ftw.footer.interfaces import IFooterSettings
from ftw.footer.interfaces import IFtwFooterLayer
from ftw.footer.testing import FTW_FOOTER_INTEGRATION_TESTING
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.registry.interfaces import IRegistry
from Products.Five.browser import BrowserView
from pyquery import PyQuery
from unittest2 import TestCase
from zope.component import getUtility
from zope.component import queryMultiAdapter
from zope.interface import alsoProvides
from zope.viewlet.interfaces import IViewletManager


class TestFooter(TestCase):

    layer = FTW_FOOTER_INTEGRATION_TESTING

    def setUp(self):
        super(TestFooter, self).setUp()
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def get_viewlet(self, context):
        alsoProvides(context.REQUEST, IFtwFooterLayer)
        view = BrowserView(context, context.REQUEST)
        manager_name = 'plone.portalfooter'

        manager = queryMultiAdapter(
            (context, context.REQUEST, view),
            IViewletManager,
            manager_name)
        self.failUnless(manager)

        # Set up viewlets
        manager.update()
        name = 'ftw.footer.viewlet'
        viewlets = [v for v in manager.viewlets if v.__name__ == name]

        if len(viewlets) == 1:
            return viewlets[0]
        return None

    def test_viewlet_registered_on_plone_root(self):
        viewlet = self.get_viewlet(self.portal)

        self.assertTrue(viewlet, 'Viewlet is not available on portal root')

    def test_viewlet_registered_on_folder(self):
        folder = create(Builder('folder'))
        viewlet = self.get_viewlet(folder)

        self.assertTrue(viewlet, 'Viewlet is not available on portal root')

    def test_generate_classes(self):
        viewlet = self.get_viewlet(self.portal)

        self.assertEqual('column cell position-0 width-4',
                         viewlet.generate_classes('ftw.footer.column1'))
        self.assertEqual('column cell position-4 width-4',
                         viewlet.generate_classes('ftw.footer.column2'))
        self.assertEqual('column cell position-8 width-4',
                         viewlet.generate_classes('ftw.footer.column3'))
        self.assertEqual('column cell position-12 width-4',
                         viewlet.generate_classes('ftw.footer.column4'))

    def test_calculate_index(self):
        viewlet = self.get_viewlet(self.portal)

        self.assertEqual(12, viewlet.calculate_index('ftw.footer.column4'))
        self.assertEqual(8, viewlet.calculate_index('ftw.footer.column3'))
        self.assertEqual(4, viewlet.calculate_index('ftw.footer.column2'))
        self.assertEqual(0, viewlet.calculate_index('ftw.footer.column1'))

    def test_is_column_visible(self):
        viewlet = self.get_viewlet(self.portal)

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IFooterSettings)
        proxy.columns_count = 2

        self.assertEqual(viewlet.is_column_visible(1), True)
        self.assertEqual(viewlet.is_column_visible(2), True)
        self.assertEqual(viewlet.is_column_visible(3), False)
        self.assertEqual(viewlet.is_column_visible(4), False)

    def test_calculate_width(self):
        viewlet = self.get_viewlet(self.portal)
        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IFooterSettings)

        self.assertEqual(4, viewlet.calculate_width())

        proxy.columns_count = 2
        self.assertEqual(8, viewlet.calculate_width())

        proxy.columns_count = 1
        self.assertEqual(16, viewlet.calculate_width())

    def test_css_classes(self):
        viewlet = self.get_viewlet(self.portal)

        registry = getUtility(IRegistry)
        proxy = registry.forInterface(IFooterSettings)

        proxy.columns_count = 2

        doc = PyQuery(viewlet.render())
        footer = doc('#ftw-footer')
        child = footer.children()[0]
        child = PyQuery(child)

        self.assertEqual(child.attr('class'), 'column cell position-0 width-8')

        child = footer.children()[1]
        child = PyQuery(child)
        self.assertEqual(child.attr('class'), 'column cell position-8 width-8')

    def test_CAN_manager_footer(self):
        viewlet = self.get_viewlet(self.portal)
        self.assertTrue(viewlet.has_permission())

    def test_CANNOT_manage_footer(self):
        viewlet = self.get_viewlet(self.portal)

        self.portal.manage_permission('ftw.footer: Manage Footer',
                                       roles=[])
        self.assertFalse(viewlet.has_permission())
