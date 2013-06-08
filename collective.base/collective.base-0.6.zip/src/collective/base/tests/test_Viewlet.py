from collective.base.interfaces import IViewlet
from collective.base.tests.base import IntegrationTestCase
from collective.base.viewlet import Viewlet

import mock


class ViewletTestCase(IntegrationTestCase):
    """TestCase for Viewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase as Base
        self.assertTrue(issubclass(Viewlet, Base))
        from zope.viewlet.interfaces import IViewlet as Base
        self.assertTrue(issubclass(IViewlet, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(Viewlet)
        self.assertTrue(verifyObject(IViewlet, instance))

    def test_repeated(self):
        instance = self.create_viewlet(Viewlet)
        with self.assertRaises(NotImplementedError):
            instance.repeated()

        instance._handle_repeated = mock.Mock()
        instance.render = mock.Mock()
        instance.repeated()
        self.assertTrue(instance.render.called)

    def test_available(self):
        instance = self.create_viewlet(Viewlet)
        self.assertTrue(instance.available())
