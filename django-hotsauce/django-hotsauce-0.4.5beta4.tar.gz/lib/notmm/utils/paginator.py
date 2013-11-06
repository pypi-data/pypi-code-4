#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webhelpers.paginate import Page

__all__ = ['getpaginator', 'getpageinfo']

# Thanks to the webhelpers.paginate authors for providing a 
# reliable paginator algorithm
def getpaginator(items, settings, paginator=Page):

    return paginator(items, 
        page=settings.BLOGENGINE['PAGE_MAX'], 
        items_per_page=settings.BLOGENGINE['ITEMS_PER_PAGE'])

def getpageinfo(p):
    """Return the next and prev page from the ``p`` instance."""
    if p.page == p.page_count:
        next_page = p.first_page
    else:
        next_page = p.page + 1
    
    if p.page == 1:
        prev_page = p.page
    else:
        prev_page = p.page - 1

    return (next_page, prev_page)

