from Products.CMFCore.utils import getToolByName
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from collective.base.viewlet import Viewlet
from collective.cart.core.browser.interfaces import IAddToCartViewlet
from collective.cart.core.browser.interfaces import ICartArticleListingViewlet
from collective.cart.core.browser.interfaces import IOrderArticleListingViewlet
from collective.cart.core.browser.interfaces import IOrderListingViewlet
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.interfaces import IOrder
from collective.cart.core.interfaces import IOrderContainerAdapter
from collective.cart.core.interfaces import IShoppingSite
from zExceptions import Forbidden
from zope.interface import implements
from zope.lifecycleevent import modified


class AddToCartViewlet(Viewlet):
    """Viewlet to display add to cart form for article"""
    implements(IAddToCartViewlet)
    index = ViewPageTemplateFile('viewlets/add-to-cart.pt')

    def update(self):
        form = self.request.form
        if form.get('form.buttons.AddToCart', None) is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            IArticleAdapter(self.context).add_to_cart()
            context_state = self.context.restrictedTraverse('@@plone_context_state')
            return self.request.response.redirect(context_state.current_base_url())

    def available(self):
        """Returns True if availabel else False

        :rtype: bool
        """
        return IArticleAdapter(self.context).addable_to_cart()


class CartArticleListingViewlet(Viewlet):
    """Viewlet to display articles in cart"""
    implements(ICartArticleListingViewlet)
    index = ViewPageTemplateFile('viewlets/cart-article-listing.pt')

    def articles(self):
        """Returns list of articles in cart

        :rtype: list
        """
        return IShoppingSite(self.context).cart_article_listing()

    def update(self):
        form = self.request.form
        uuid = form.get('form.buttons.RemoveArticle', None)

        if uuid is not None:

            authenticator = self.context.restrictedTraverse('@@authenticator')
            if not authenticator.verify():
                raise Forbidden()

            shopping_site = IShoppingSite(self.context)
            shopping_site.remove_cart_articles(uuid)
            if not shopping_site.cart_articles():
                current_base_url = self.context.restrictedTraverse("plone_context_state").current_base_url()
                return self.request.response.redirect(current_base_url)


class OrderListingViewlet(Viewlet):
    """Viewlet for content type: collective.cart.core.OrderContent"""
    implements(IOrderListingViewlet)
    index = ViewPageTemplateFile('viewlets/order-listing.pt')

    def _transitions(self, item):
        workflow = getToolByName(self.context, 'portal_workflow')
        obj = item.getObject()
        res = []
        for trans in workflow.getTransitionsFor(obj):
            available = True
            if item.review_state() == 'created' and trans['id'] != 'canceled':
                available = False
            res.append({
                'id': trans['id'],
                'name': trans['name'],
                'available': available,
            })
        return res

    def container(self):
        return IShoppingSite(self.context).order_container()

    def orders(self):
        container = self.container()
        result = []
        if container:
            workflow = getToolByName(self.context, 'portal_workflow')
            adapter = IOrderContainerAdapter(container)
            toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
            for item in adapter.get_content_listing(IOrder, depth=1, sort_on="modified", sort_order="descending"):
                res = {
                    'id': item.getId(),
                    'title': item.Title(),
                    'url': item.getURL(),
                    'state_title': workflow.getTitleForStateOnType(item.review_state(), item.portal_type),
                    'modified': toLocalizedTime(item.ModificationDate()),
                    'owner': item.Creator(),
                    'transitions': self._transitions(item),
                    'is_canceled': item.review_state() == 'canceled',
                }
                result.append(res)
        return result

    def update(self):
        form = self.request.form
        url = self.context.restrictedTraverse('@@plone_context_state').current_base_url()

        if form.get('form.buttons.ChangeState') is not None:
            [order_id, value] = form.get('form.buttons.ChangeState').split(':')
            order = IShoppingSite(self.context).get_order(order_id)
            if order:
                workflow = getToolByName(self.context, 'portal_workflow')
                workflow.doActionFor(order, value)
                modified(order)

                return self.request.response.redirect(url)

        elif form.get('form.buttons.RemoveOrder') is not None:
            order_id = form.get('form.buttons.RemoveOrder')
            self.container().manage_delObjects([order_id])

            return self.request.response.redirect(url)


class OrderArticleListingViewlet(Viewlet):
    """Viewlet to display articles in order"""
    implements(IOrderArticleListingViewlet)
    index = ViewPageTemplateFile('viewlets/order-article-listing.pt')
