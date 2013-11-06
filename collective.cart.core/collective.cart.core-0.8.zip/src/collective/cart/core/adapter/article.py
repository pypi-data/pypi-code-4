from collective.base.adapter import Adapter
from collective.behavior.salable.interfaces import ISalable
from collective.cart.core.interfaces import IArticle
from collective.cart.core.interfaces import IArticleAdapter
from collective.cart.core.interfaces import IShoppingSite
from collective.cart.core.session import SessionArticles
from plone.uuid.interfaces import IUUID
from zope.component import adapts
from zope.interface import implements


class ArticleAdapter(Adapter):
    """Adapter for collective.cart.core.Article"""

    adapts(IArticle)
    implements(IArticleAdapter)

    def addable_to_cart(self):
        """Returns True if the Article is addable to cart else False

        :rtype: bool
        """
        return ISalable(self.context).salable

    def _update_existing_cart_article(self, items, **kwargs):
        """Update cart article which already exists in current cart.
        """

    def add_to_cart(self, **kwargs):
        """Add Article to cart"""
        shopping_site = IShoppingSite(self.context)
        cart = shopping_site.cart()
        if cart is None:
            session = self.getSessionData(create=True)
            session.set('collective.cart.core', {})
        else:
            session = self.getSessionData(create=False)

        articles = IShoppingSite(self.context).cart_articles()
        if not articles:
            articles = SessionArticles()

        uuid = IUUID(self.context)

        if uuid in articles:
            items = articles[uuid]
            self._update_existing_cart_article(items, **kwargs)

        else:
            items = {
                'id': uuid,
                'title': self.context.Title(),
                'description': self.context.Description(),
                'url': self.context.absolute_url(),
            }
            items.update(kwargs)

        articles[uuid] = items
        shopping_site.update_cart('articles', articles)
