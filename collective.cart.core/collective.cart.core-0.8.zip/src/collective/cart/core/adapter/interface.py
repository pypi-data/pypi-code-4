from Acquisition import aq_chain
from Acquisition import aq_inner
from collective.base.adapter import Adapter
from collective.cart.core.interfaces import IOrder
from collective.cart.core.interfaces import IOrderContainer
from collective.cart.core.interfaces import IOrderContainerAdapter
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.interfaces import IShoppingSiteRoot
from plone.dexterity.utils import createContentInContainer
from zope.interface import implements
from zope.lifecycleevent import modified


class ShoppingSite(Adapter):
    """Adapter for shopping site"""

    implements(IShoppingSite)

    def shop(self):
        """Returns Shopping site root object

        :rtype: object provides collective.cart.core.interfaces.IShoppingSiteRoot
        """
        context = aq_inner(self.context)
        chain = aq_chain(context)
        shops = [obj for obj in chain if IShoppingSiteRoot.providedBy(obj)]
        if shops:
            return shops[0]

    def shop_path(self):
        """Returns path of shopping site root

        :rtype: string
        """
        if self.shop():
            return '/'.join(self.shop().getPhysicalPath())

    def order_container(self):
        """Returns order container located directly under shopping site root

        :rtype: collective.cart.core.OrderContainer
        """
        if self.shop():
            return self.get_object(IOrderContainer, path=self.shop_path(), depth=1)

    def cart(self):
        """Returns cart in session

        :rtype: dict
        """
        session = self.getSessionData(create=False)
        if session:
            return session.get('collective.cart.core')

    def cart_articles(self):
        """Returns list of ordered dictionary of cart articles in session

        :rtype: dict
        """
        if self.cart():
            return self.cart().get('articles')

    def cart_article_listing(self):
        """Returns list of cart articles in session for view

        :rtype: list
        """
        res = []
        articles = self.cart_articles()
        if articles:
            for key in articles:
                res.append(articles[key])
        return res

    def get_cart_article(self, uuid):
        """Returns dictionary of cart article by uuid

        :param uuid: UUID
        :type uuid: str

        :rtype: dict
        """
        if self.cart_articles():
            return self.cart_articles().get(uuid)

    def remove_cart_articles(self, uuids):
        """Removes articles of uuids from cart

        :param uuids: List of uuids or  in string.
        :type uuids: list or str

        :rtype: list
        """
        articles = self.cart_articles()
        deleted = []
        if articles:
            if isinstance(uuids, str):
                uuids = [uuids]
            for uuid in uuids:
                deleting = articles.pop(uuid, None)
                if deleting is not None:
                    deleted.append(deleting)
            if deleted:
                session = self.getSessionData(create=False)
                if session:
                    cart = session.get('collective.cart.core')
                    cart['articles'] = articles
                    session.set('collective.cart.core', cart)
        return deleted

    def update_cart(self, name, items):
        """Update cart by name and items

        :param name: key of cart content
        :type name: str

        :param items: value of cart content
        :type items: dict
        """
        cart = self.cart()
        if cart is not None:
            cart[name] = items
            session = self.getSessionData(create=False)
            session.set('collective.cart.core', cart)

    def remove_from_cart(self, name):
        """Removes name from cart

        :param name: key of cart content
        :type name: str

        :rtype: dict
        """
        cart = self.cart()
        if cart:
            values = cart.pop(name, None)
            session = self.getSessionData(create=False)
            session.set('collective.cart.core', cart)
            return values

    def clear_cart(self):
        """Clear cart from session"""
        cart = self.cart()
        if cart is not None:
            session = self.getSessionData(create=False)
            del session['collective.cart.core']

    def clean_articles_in_cart(self):
        """Clean articles in cart like:

        Remove article from cart if article no longer exist in shop.

        :rtype: list
        """
        cart_articles = self.cart_articles()
        if cart_articles:
            articles = cart_articles.copy()
            number_of_articles = len(articles)
            for key in cart_articles:
                if not self.get_brain(UID=key):
                    del articles[key]

            if len(articles) != number_of_articles:
                self.update_cart('articles', articles)

            return articles

    # OrderContainer related methods comes here::

    def get_order(self, order_id):
        """Returns order by its id

        :param order_id: Order ID
        :type order_id: str

        :rtype: collective.cart.core.Order
        """
        if self.order_container():
            container_path = '/'.join(self.order_container().getPhysicalPath())
            return self.get_object(IOrder, id=order_id, path=container_path, depth=1, unrestricted=True)

    def update_next_order_id(self):
        """Update next order ID for the order container"""
        container = self.order_container()
        if container:
            IOrderContainerAdapter(container).update_next_order_id()

    def create_order(self, order_id=None):
        """Create order into order container from cart in session

        :param order_id: Order ID
        :type order_id: str

        :rtype: collective.cart.core.Order
        """
        container = self.order_container()
        articles = self.cart_articles()
        if container and articles:
            if order_id is None:
                order_id = str(container.next_order_id)
            order = createContentInContainer(
                container, 'collective.cart.core.Order', id=order_id, checkConstraints=False)
            modified(order)
            self.update_next_order_id()
            for uuid in articles:
                article = createContentInContainer(order, 'collective.cart.core.OrderArticle', checkConstraints=False, **articles[uuid])
                modified(article)

            return order
