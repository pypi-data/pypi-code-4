from collective.base.interfaces import IBaseFormView
from collective.base.view import BaseFormView
from collective.base.tests.base import IntegrationTestCase


class BaseFormViewTestCase(IntegrationTestCase):
    """TestCase for BaseFormView"""

    def test_subclass(self):
        from collective.base.view import BaseView as Base
        self.assertTrue(issubclass(BaseFormView, Base))
        from collective.base.interfaces import IBaseView as Base
        self.assertTrue(issubclass(IBaseFormView, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_view(BaseFormView)
        self.assertTrue(verifyObject(IBaseFormView, instance))
