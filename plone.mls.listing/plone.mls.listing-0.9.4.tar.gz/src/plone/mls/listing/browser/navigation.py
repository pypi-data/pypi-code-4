# -*- coding: utf-8 -*-
"""Navigation Breadcrumb customizations."""

# zope imports
from Products.CMFPlone.browser.navigation import (
    get_view_url,
    PhysicalNavigationBreadcrumbs,
)


class ListingDetailsNavigationBreadcrumbs(PhysicalNavigationBreadcrumbs):
    """Custom breadcrumb navigation for listing details."""

    def breadcrumbs(self):
        base = super(ListingDetailsNavigationBreadcrumbs, self).breadcrumbs()

        name, item_url = get_view_url(self.context)

        listing_id = getattr(self.request, 'listing_id', None)
        last_item = self.request.steps[-2:-1]
        if listing_id is not None and self.context.id in last_item:
            base += ({
                'absolute_url': item_url + '/' + listing_id,
                'Title': listing_id.upper(),
            },)

        return base
