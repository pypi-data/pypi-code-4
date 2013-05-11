from collective.base.interfaces import IViewlet

import unittest


class ViewletTestCase(unittest.TestCase):
    """TestCase for Viewlet"""

    def test_subclass(self):
        from zope.viewlet.interfaces import IViewlet as IBaseViewlet
        self.assertTrue(issubclass(IViewlet, IBaseViewlet))
