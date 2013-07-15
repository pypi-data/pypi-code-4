"""this contains the cube-specific entities' classes"""

from logilab.common.decorators import cachedproperty

from cubicweb.predicates import is_instance
from cubicweb.entities import AnyEntity, fetch_config
from cubicweb.web.views.ibreadcrumbs import IBreadCrumbsAdapter

class Card(AnyEntity):
    """customized class for Card entities"""
    __regid__ = 'Card'
    rest_attr = 'wikiid'

    fetch_attrs, cw_fetch_order = fetch_config(['title'])

    def dc_title(self):
        if self.wikiid:
            return self.wikiid.split('/')[-1]
        else:
            return self.title

    def dc_description(self, format='text/plain'):
        return self.printable_value('synopsis', format=format)

    def rest_path(self, use_ext_eid=False):
        if self.wikiid:
            return '%s/%s' % (str(self.e_schema).lower(),
                              self._cw.url_quote(self.wikiid, safe='/'))
        else:
            return super(Card, self).rest_path(use_ext_eid)


class CardBreadCrumbsAdapter(IBreadCrumbsAdapter):

    __select__ = IBreadCrumbsAdapter.__select__ & is_instance('Card')

    @cachedproperty
    def dirname(self):
        if self.entity.wikiid:
            return '/'.join(self.entity.wikiid.split('/')[:-1])

    def card_from_wikiid(self, path):
        """Return the Card given its ``wikiid`` path or None"""
        rset = self._cw.execute("Card C WHERE C wikiid %(id)s", {"id": path})
        if rset:
            return rset.get_entity(0, 0)

    def parent_entity(self):
        if not self.dirname:
            # card is at root: return whatever super returns
            parent = super(CardBreadCrumbsAdapter, self).parent_entity()
        else:
            parent = self.card_from_wikiid(self.dirname)
        return parent

    def breadcrumbs(self, view=None, recurs=None):
        """Virtual hierarchy of wiki pages following a directory-like
        structure.
        """
        if self.parent_entity() or not self.dirname:
            # parent Card exists or the current Card is at the root (i.e. its
            # wikiid has no /)
            return super(CardBreadCrumbsAdapter, self).breadcrumbs(view, recurs)
        else:
            # parent card does not exist: build the (reversed) path by
            # iterating on the directory structure
            path = [self.entity]
            dirs = self.dirname.split('/')
            while dirs:
                card = self.card_from_wikiid('/'.join(dirs))
                p = [dirs.pop()]
                if card:
                    p = card.cw_adapt_to('IBreadCrumbs').breadcrumbs(view, recurs)
                path.extend(p)
            if not card:
                # last path entry is not a card
                path.append((self._cw.build_url(str(self.entity.e_schema)),
                             self._cw._('Card_plural')))
            path.reverse()
            return path

