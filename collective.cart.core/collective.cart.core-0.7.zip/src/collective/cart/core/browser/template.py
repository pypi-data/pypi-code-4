from collective.base.view import BaseFormView
from collective.cart.core import _
from collective.cart.core.browser.interfaces import ICartView
from collective.cart.core.browser.interfaces import ICheckOutView
from collective.cart.core.browser.interfaces import IOrderListingView
from collective.cart.core.browser.interfaces import IOrderView
from collective.cart.core.interfaces import IShoppingSite
from zope.interface import implements


class CheckOutView(BaseFormView):
    """Base view for check out"""

    implements(ICheckOutView)

    def __call__(self):
        super(CheckOutView, self).__call__()
        IShoppingSite(self.context).clean_articles_in_cart()


class CartView(CheckOutView):
    """view for cart"""

    title = _(u'Cart')
    implements(ICartView)

    def __call__(self):
        super(CartView, self).__call__()
        return self.template()


class OrderListingView(BaseFormView):
    """View for order listing"""

    implements(IOrderListingView)

    title = _(u'Order Listing')

    def description(self):
        """Returns description of view"""
        if self.order_container():
            return _(u'next_order_id_description', u'The next order ID: ${order_id}',
                mapping={'order_id': self.order_container().next_order_id})

    def order_container(self):
        """Returns order container"""
        return IShoppingSite(self.context).order_container()

    def __call__(self):
        self.request.set('disable_plone.leftcolumn', True)
        self.request.set('disable_plone.rightcolumn', True)
        super(OrderListingView, self).__call__()
        self.request.set('disable_border', False)

        return self.template()


class OrderView(BaseFormView):
    """View for order"""
    implements(IOrderView)

    def title(self):
        message = _(u'order_view_title', default=u'Order ID: ${order_id}', mapping={'order_id': self.context.id})
        return message

    def description(self):
        return self.context.description

    def __call__(self):
        return self.template()
