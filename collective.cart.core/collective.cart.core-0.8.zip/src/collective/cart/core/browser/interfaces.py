from collective.base.interfaces import IBaseFormView
from collective.base.interfaces import IViewlet
from zope.interface import Interface
from zope.viewlet.interfaces import IViewletManager


# Browser layer

class ICollectiveCartCoreLayer(Interface):
    """Interface for browserlayer."""


# Viewlet manager

class IOrderViewletManager(IViewletManager):
    """Viewlet manager interface for order"""


# View

class ICheckOutView(IBaseFormView):
    """View interface for check out"""


class ICartView(ICheckOutView):
    """View interface for cart"""


class IOrderListingView(IBaseFormView):
    """View interface for order listing"""

    def order_container():
        """Returns order container"""


class IOrderView(IBaseFormView):
    """View interface for order"""


# Viewlet

class IAddToCartViewlet(IViewlet):
    """Viewlet interface for AddToCartViewlet"""

    def available():
        """Returns True if availabel else False"""


class ICartArticleListingViewlet(IViewlet):
    """Viewlet interface for CartArticleListingViewlet"""

    def articles():
        """Returns list of articles in cart"""


class IOrderListingViewlet(IViewlet):
    """Viewlet interface for OrderListingViewlet"""

    def container():
        """Returns order container object

        :rtype: collective.cart.core.Ordercontainer
        """

    def orders():
        """Returns list of oders

        :rtype: list
        """


class IOrderArticleListingViewlet(IViewlet):
    """Viewlet interface for OrderArticleListingViewlet"""
