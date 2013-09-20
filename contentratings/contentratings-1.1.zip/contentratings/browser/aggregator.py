from zope.component import getAdapters, getMultiAdapter, queryMultiAdapter
from contentratings.interfaces import IUserRating, IEditorialRating

def get_rating_categories(context, interface):
    """Finds all named rating categories for the object matching
    the classes RATING_IFACE, and returns them in order"""
    adapters = getAdapters((context,), interface)
    return sorted((a for n, a in adapters), key=lambda x: x.order)

class UserRatingAggregatorView(object):
    """View which combines the views of each IUserRating category for a given
    context"""
    RATING_IFACE = IUserRating
    CLASS_NAME = 'UserRatings'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def _get_view(self, manager):
        return getMultiAdapter((manager, self.request), name=manager.view_name)

    def __call__(self):
        """Returns a simple div containing all of the ordered rating category
        views"""
        categories = get_rating_categories(self.context, self.RATING_IFACE)
        # Get the views for each manager if they exist and are not empty
        rendered = list(c for c in (v() for v in
                                   (self._get_view(m) for m in categories) if v)
                        if c.strip())
        if not rendered:
            return u''
        return u'<div class="%s">%s</div>'%(self.CLASS_NAME,
                                            '\n'.join(rendered))


class UserRatingAggregatorReadView(UserRatingAggregatorView):
    """Aggregates the UserRating read views for available categories"""
    def _get_view(self, manager):
        """Read views are found via convention: view_name + '_read'"""
        return queryMultiAdapter((manager, self.request),
                                 name=manager.view_name+'_read')


class EditorialRatingAggregatorView(UserRatingAggregatorView):
    """View which combines the views of each IEditorialRating category
    for a given context"""
    RATING_IFACE = IEditorialRating
    CLASS_NAME = 'EditorialRatings'


class EditorialRatingAggregatorReadView(UserRatingAggregatorReadView):
    """View which combines the read views of each IEditorialRating category
    for a given context"""
    RATING_IFACE = IEditorialRating
    CLASS_NAME = 'EditorialRatings'
