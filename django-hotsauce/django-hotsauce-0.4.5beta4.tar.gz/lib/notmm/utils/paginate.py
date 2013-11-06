#!/usr/bin/env python
# -*- coding: utf-8 -*-

from webhelpers.paginate import Page

__all__ = ['paginate']

# Thanks to the webhelpers.paginate authors for providing a 
# reliable paginator algorithm
def paginate(items, settings):

    p = Page(items, page=settings.BLOGENGINE['PAGE_MAX'], 
        items_per_page=settings.BLOGENGINE['ITEMS_PER_PAGE'])

    if p.page == p.page_count:
        next_page = p.first_page
    else:
        next_page = p.page + 1
    
    if p.page == 1:
        prev_page = p.page
    else:
        prev_page = p.page - 1

    return (p, next_page, prev_page)

