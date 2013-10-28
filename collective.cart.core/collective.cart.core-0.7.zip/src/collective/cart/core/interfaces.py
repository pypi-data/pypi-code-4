from collective.base.interfaces import IAdapter
from collective.cart.core.schema import ArticleSchema
from collective.cart.core.schema import OrderArticleSchema
from collective.cart.core.schema import OrderContainerSchema
from collective.cart.core.schema import OrderSchema
from plone.dexterity.interfaces import IDexterityContainer
from zope.interface import Interface


# Content type

class IArticle(ArticleSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.Article"""


class IOrderContainer(OrderContainerSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.OrderContainer"""


class IOrder(OrderSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.Order"""


class IOrderArticle(OrderArticleSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.OrderArticle"""


# Deprecated

class ICartContainer(OrderContainerSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.CartContainer"""


class ICart(OrderSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.Cart"""


class ICartArticle(OrderArticleSchema, IDexterityContainer):
    """Interface for content type: collective.cart.core.CartArticle"""


# Adapter

class IShoppingSiteRoot(Interface):
    """Marker interface for Shopping Site Root"""


class IShoppingSite(IAdapter):
    """Adapter interface for Shopping Site."""

    def shop():  # pragma: no cover
        """Returns Shopping site root object"""

    def shop_path():  # pragma: no cover
        """Returns path of shopping site root"""

    def order_container():  # pragma: no cover
        """Returns order container located directly under shopping site root"""

    def cart():  # pragma: no cover
        """Returns cart in session"""

    def cart_articles():  # pragma: no cover
        """Returns list of ordered dictionary of cart articles in session"""

    def cart_article_listing():  # pragma: no cover
        """Returns list of cart articles in session for view"""

    def get_cart_article(uuid):  # pragma: no cover
        """Returns dictionary of cart article by uuid"""

    def remove_cart_articles(uuids):  # pragma: no cover
        """Removes articles of uuids from cart"""

    def update_cart(name, items):  # pragma: no cover
        """Update cart by name and items"""

    def remove_from_cart(name):  # pragma: no cover
        """Remove name from cart"""

    def clear_cart():  # pragma: no cover
        """Clear cart from session"""

    def clean_articles_in_cart():  # pragma: no cover
        """Clean articles in cart like:

        Remove article from cart if article no longer exist in shop.
        """

    # OrderContainer related methods comes here::

    def get_order(order_id):  # pragma: no cover
        """Returns order by its id"""

    def update_next_order_id():  # pragma: no cover
        """Update next order ID for the order container"""

    def create_order(order_id=None):  # pragma: no cover
        """Create order into order container from cart in session"""


class IOrderContainerAdapter(IAdapter):
    """Adapter Interface for CartContainer."""

    def update_next_order_id():  # pragma: no cover
        """Update next_order_id"""


class IOrderAdapter(IAdapter):
    """Adapter interface for Cart."""

    def articles():  # pragma: no cover
        """Returns list of brains of OrderArticle"""

    def get_article(oid):  # pragma: no cover
        """Returns CartArticle form order by ID"""


class IArticleAdapter(IAdapter):
    """Adapter Interface for Article."""

    def addable_to_cart():  # pragma: no cover
        """Returns True if the Article is addable to cart else False"""

    def add_to_cart():  # pragma: no cover
        """Add Article to cart"""


class IMakeShoppingSiteEvent(Interface):
    """An event making shopping site."""


class IUnmakeShoppingSiteEvent(Interface):
    """An event unmaking shopping site."""


class ISessionArticles(Interface):
    """Interface for cart in session."""
