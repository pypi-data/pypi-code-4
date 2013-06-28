# -*- coding: utf-8 -*-
"""Custom Traverser implementation for IRecentListings."""

# zope imports
from ZPublisher.BaseRequest import DefaultPublishTraverse
from zope.component import queryMultiAdapter
from zope.publisher.interfaces import NotFound


class RecentListingsTraverser(DefaultPublishTraverse):
    """Custom Traverser for IRecentListings."""

    def publishTraverse(self, request, name):
        """See zope.publisher.interfaces.IPublishTraverse"""
        # Try to deliver the default content views.
        try:
            return super(RecentListingsTraverser, self).publishTraverse(
                request, name)
        except (NotFound, AttributeError):

            # We store the listing_id parameter in the request.
            self.request.listing_id = name
            listing_view = 'listing-detail'
            default_view = self.context.getDefaultLayout()

            # Let's call the listing view.
            view = queryMultiAdapter((self.context, request),
                                     name=listing_view)
            if view is not None:
                return view

            # Deliver the default item view as fallback.
            view = queryMultiAdapter((self.context, request),
                                     name=default_view)
            if view is not None:
                return view

        raise NotFound(self.context, name, request)
