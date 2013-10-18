"""Packaging Operators describe how the query ``result set`` is presented.
Use these as ``filters`` on the ``eql.Query`` object.
"""

from echo.eql.filters import QueryFilter
import datetime

# ======================================================================
# Packaging Operators as Filters
# ======================================================================

class ItemsPerPageFilter(QueryFilter):
    """ This is the packaging operator ``itemsPerPage``.
    Use this filter to change the number of items returned by the query.
    ``itemsPerPage`` is a positive integer, default 15.
    The maximum ``itemsPerPage`` is 100 unless Echo configures it's servers otherwise.
    """
    def __init__(self, filter_values=15):
        try:
            itemsPerPage = int(filter_values)
            if itemsPerPage < 0:
                raise ValueError('not a positive integer')
        except (ValueError, TypeError), e:
            raise TypeError('Invalid itemsPerPage %r "%s".' % (filter_values, str(e)))
        # NOTE: Convert itemsPerPage to string or TypeError occurs in
        # superclass.
        super(ItemsPerPageFilter, self).__init__('itemsPerPage',
                                         filter_values=[str(itemsPerPage)])

class PageAfterFilter(QueryFilter):
    """ This filter specifies the criteria to select the next portion
    of the items within the same data set.

    The "pageAfter" predicate value should be used to get the next portion of the items.
    It is returned in the current search result in the ``nextPageAfter`` field.

    Make additional request with the ``pageAfter`` predicate and the ``nextPageAfter``
    value from the previous request to select the next portion of items.
    Make several requests until the search result returns an empty set of items.

    This can work one of two ways, either by giving it a straight-up timestamp for
    chronological searches, or by giving it "<timestamp>|<count>" for searches with
    likes/replies/flags decending.
    """
    def __init__(self, filter_value=None):
        try:
            if "|" in filter_value:
                pageAfter = str(filter_value).split('|')
                tstamp = pageAfter[0]
                float(tstamp)
                likes_count = pageAfter[1]
                int(likes_count)
                filter_value = "%s|%s" % (tstamp, likes_count)
            else:
                float(filter_value)
        except (IndexError, ValueError, TypeError), e:
            raise TypeError('Invalid pageAfter %r "%s".' % (filter_value, str(e)))
        super(PageAfterFilter, self).__init__('pageAfter',
                                              filter_values=[str(filter_value).strip()])

# ======================================================================
# Time Operators
# ======================================================================

class afterFilter(QueryFilter):
    """ This is a filter that grabs all stories after a datetime """
    def __init__(self, filter_value=None):
        if type(filter_value) != datetime.datetime:
            raise TypeError("Filter value must be a datetime")
        datestring = filter_value.strftime("%Y-%m-%dT%H:%M:%S")
        super(afterFilter, self).__init__('after', filter_values=['"%s"' % datestring,])

class beforeFilter(QueryFilter):
    """ This is a filter that grabs all stories before a datetime """
    def __init__(self, filter_value=None):
        if type(filter_value) != datetime.datetime:
            raise TypeError("Filter value must be a datetime")
        datestring = filter_value.strftime("%Y-%m-%dT%H:%M:%S")
        super(beforeFilter, self).__init__('before', filter_values=['"%s"' % datestring,])

# ======================================================================

if __name__ == "__main__":

    # ItemsPerPageFilter test:
    items_per_page_filter = ItemsPerPageFilter(35)
    print "ItemsPerPageFilter: %r" % items_per_page_filter

    # PageAfterFilter test:
    page_after_filter = PageAfterFilter('  12345678.0123|31 ')
    print "PageAfterFilter: %r" % page_after_filter

    # afterFilter test
    after_filter = afterFilter(datetime.datetime.now())
    print "afterFilter: %r" % after_filter

    # beforeFilter test
    before_filter = beforeFilter(datetime.datetime.now())
    print "beforeFilter: %r" % before_filter

