from collective.base.interfaces import IBaseView
from collective.base.view import BaseView
from collective.base.tests.base import IntegrationTestCase


class BaseViewTestCase(IntegrationTestCase):
    """TestCase for BaseView"""

    def test_subclass(self):
        from Products.Five import BrowserView as Base
        self.assertTrue(issubclass(BaseView, Base))
        from plone.app.layout.globals.interfaces import IViewView as Base
        self.assertTrue(issubclass(IBaseView, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(BaseView)
        self.assertTrue(verifyObject(IBaseView, instance))

    def test___call__(self):
        instance = self.create_view(BaseView)
        self.assertIsNone(instance())
        self.assertTrue(instance.request.get('disable_border'))
