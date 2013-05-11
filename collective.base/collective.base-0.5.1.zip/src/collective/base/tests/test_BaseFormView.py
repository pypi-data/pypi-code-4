from collective.base.interfaces import IBaseFormView
from collective.base.view import BaseFormView
from collective.base.tests.base import IntegrationTestCase


class BaseFormViewTestCase(IntegrationTestCase):
    """TestCase for BaseFormView"""

    def test_subclass(self):
        from Products.Five import BrowserView
        self.assertTrue(issubclass(BaseFormView, BrowserView))
        from plone.app.layout.globals.interfaces import IViewView
        self.assertTrue(issubclass(IBaseFormView, IViewView))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(BaseFormView)
        self.assertTrue(verifyObject(IBaseFormView, instance))

    def test___call__(self):
        instance = self.create_view(BaseFormView)
        self.assertIsNone(instance())
        instance.request.set.assert_called_with('disable_border', True)
