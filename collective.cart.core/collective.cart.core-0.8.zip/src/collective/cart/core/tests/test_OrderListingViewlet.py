# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from collective.cart.core.browser.interfaces import IOrderListingViewlet
from collective.cart.core.browser.viewlet import OrderListingViewlet
from collective.cart.core.interfaces import IShoppingSiteRoot
from collective.cart.core.tests.base import IntegrationTestCase
from zope.interface import alsoProvides

import mock


class OrderListingViewletTestCase(IntegrationTestCase):
    """TestCase for OrderListingViewlet"""

    def test_subclass(self):
        from plone.app.layout.viewlets.common import ViewletBase
        self.assertTrue(issubclass(OrderListingViewlet, ViewletBase))
        from collective.cart.core.browser.interfaces import IViewlet
        self.assertTrue(issubclass(IOrderListingViewlet, IViewlet))

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        instance = self.create_viewlet(OrderListingViewlet)
        self.assertTrue(verifyObject(IOrderListingViewlet, instance))

    @mock.patch('collective.cart.core.browser.viewlet.IShoppingSite')
    def test_update(self, IShoppingSite):
        alsoProvides(self.portal, IShoppingSiteRoot)
        container = self.create_content('collective.cart.core.OrderContainer')
        instance = self.create_viewlet(OrderListingViewlet, container)
        workflow = getToolByName(self.portal, 'portal_workflow')
        order1 = self.create_content('collective.cart.core.Order', container, id='1')
        order2 = self.create_content('collective.cart.core.Order', container, id='2')
        workflow = getToolByName(self.portal, 'portal_workflow')
        self.assertEqual(workflow.getInfoFor(order1, 'review_state'), 'created')
        self.assertEqual(workflow.getInfoFor(order2, 'review_state'), 'created')
        self.assertIsNone(instance.update())

        self.assertEqual(workflow.getInfoFor(order1, 'review_state'), 'created')
        self.assertEqual(workflow.getInfoFor(order2, 'review_state'), 'created')

        change_state = '{}:ordered'.format(order1.id)
        instance.request.form = {'form.buttons.ChangeState': change_state}
        instance.context.restrictedTraverse = mock.Mock()
        instance.context.restrictedTraverse().current_base_url.return_value = 'CURRENT_BASE_URL'
        IShoppingSite().get_order.return_value = order1
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
        self.assertEqual(len(container.objectIds()), 2)
        self.assertEqual(workflow.getInfoFor(order1, 'review_state'), 'ordered')
        self.assertEqual(workflow.getInfoFor(order2, 'review_state'), 'created')

        IShoppingSite().order_container.return_value = container
        instance.request.form = {'form.buttons.RemoveOrder': '1'}
        self.assertEqual(instance.update(), 'CURRENT_BASE_URL')
        self.assertEqual(container.objectIds(), ['2'])
        self.assertEqual(workflow.getInfoFor(order2, 'review_state'), 'created')
