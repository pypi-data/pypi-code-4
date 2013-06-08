from collective.base.interfaces import IRepeatedViewletManager
from collective.base.viewletmanager import RepeatedViewletManager

import mock
import unittest


class RepeatedViewletManagerTestCase(unittest.TestCase):
    """TestCase for RepeatedViewletManager"""

    def test_subclass(self):
        from plone.app.viewletmanager.manager import OrderedViewletManager as Base
        self.assertTrue(issubclass(RepeatedViewletManager, Base))
        from zope.viewlet.interfaces import IViewletManager as Base
        self.assertTrue(issubclass(IRepeatedViewletManager, Base))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        context = mock.Mock()
        instance = RepeatedViewletManager(context, None, None)
        self.assertTrue(verifyObject(IRepeatedViewletManager, instance))

    def test_items(self):
        context = mock.Mock()
        instance = RepeatedViewletManager(context, None, None)
        with self.assertRaises(NotImplementedError):
            instance.items()
