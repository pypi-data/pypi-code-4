""" Filtering by Basic Criteria

The "children"/"children:N" operator divides the query string into two parts.
The first part is called "root nodes selector" and is used for finding root items.
The second part is called "children nodes selector" and is used for selecting children nodes
of the root nodes found before. Filters are applied to this concept to limit the results
by types, states, sources, as provided in this module.

A QueryFilter object creates valid filters, positive or negative ones, as EQL substrings.

Here is the simplest example with the "type" filter. It gets the articles as root nodes and all other item types as their children:

query="scope:http://example.com/* type:article"

This EQL fetches only comments as children of the articles:

query="scope:http://example.com/* type:article children type:comment"
"""

class QueryFilter(object):
    # Abstract base class for all the filter types.
    def __init__(self, filter_name, filter_values=[], allowable_values=[]):
        # NOTE: allowable_values must be defined before filter_values!
        self.allowable_values = allowable_values
        self.filter_name = filter_name
        self.filter_values = []
        self._negative = False
        self.add_values(filter_values)

    def _allowable_value(self, value):
        if self.allowable_values and value not in self.allowable_values:
            raise TypeError("%s: Invalid filter value %r" % (self.__class__.__name__, value))

    def add_values(self, values):
        """ Add one or more allowable values to this Filter. """
        # Add values; either a list or a singleton.
        # Validate all values as allowable_values.
        if isinstance(values, (list, tuple)):
            for value in values:
                self._allowable_value(value)
            self.filter_values.extend(values)
        else:
            self._allowable_value(values)
            self.filter_values.append(values)

    def _copy(self):
        # Deep copy QueryFilter with constructor...(dumb but works).
        return self.__class__(self.filter_values)

    # Negative Filter: True == ON, False == OFF.
    def _get_negative(self): return self._negative
    def _set_negative(self, bool_value):
        self._negative = bool_value
    negative = property(_get_negative, _set_negative)

    def __neg__(self):
        """ Negate this QueryFilter object.
        Always sets it to negative and does not toggle.
        """
        qf = self._copy()
        qf.negative = True
        return qf

    def __str__(self):
        """ This EQL substring is added to a query. """
        # (negation '-', name, values-comma-list)
        return "%s%s:%s" % ('-' if self.negative else '', self.filter_name, ','.join(self.filter_values))

    def __repr__(self):
        """ This describes the Filter's EQL substring. """
        return "%s: %r" % (self.__class__.__name__, str(self))

    def __and__(self, filter):
        """ Logical AND: Combine two QueryFilter objects using the & operator.
        AND is implied in EQL filters, but the & operator also groups in parentheses. 
        filter1 & filter2 & filter3
        """
        if not isinstance(filter, (QueryFilter, CompoundQueryFilter)):
            return TypeError("AND Compound Filter needs QueryFilter, not %s" % filter.__class__.__name__)
        return CompoundQueryFilter(self, filter, is_and=True)

    def __rand__(self, filter):
        # NOTE: use "__rand__" so that CompoundQueryFilter can be first operand.
        return self.__and__(filter)

    def __or__(self, filter):
        """ Logical OR: Combine two QueryFilter objects using the | operator.
        filter1 | (filter2 | filter3)
        """
        if not isinstance(filter, (QueryFilter, CompoundQueryFilter)):
            return TypeError("OR Compound Filter needs QueryFilter, not %s" % filter.__class__.__name__)
        return CompoundQueryFilter(self, filter, is_and=False)

    def __ror__(self, filter):
        # NOTE: use "__ror__" so that CompoundQueryFilter can be first operand.
        return self.__or__(filter)

# ======================================================================
# Search Operators: Filters the result set.
# ======================================================================

TYPE_FILTERS = [ 'article', 'comment', 'note', 'status' ]
class TypeFilter(QueryFilter):
    """ Searches for the items of the specified type URI.
    You can find more than one type using a filter_values list.
    For the supported types please refer to echo.eql.filters.TYPE_FILTERS
    """
    def __init__(self, filter_values=[]):
        super(TypeFilter, self).__init__('type', filter_values=filter_values,
                                         allowable_values=TYPE_FILTERS)

STATE_FILTERS = [ 'Untouched', 'SystemFlagged', 'CommunityFlagged',
                  'ModeratorFlagged', 'ModeratorDeleted', 'ModeratorApproved' ]
class StateFilter(QueryFilter):
    """ Searches for the items with the specified state. 
    You can find more than one state using a filter_values list.
    If the state predicate is omitted in the root selector part of the query, items with any states are selected.
    For the supported types please refer to echo.eql.filters.STATE_FILTERS
    """
    def __init__(self, filter_values=[]):
        super(StateFilter, self).__init__('state', filter_values=filter_values,
                                         allowable_values=STATE_FILTERS)

# NOTE: The "source" filter values are application dependent.
SOURCE_FILTERS = []
class SourceFilter(QueryFilter):
    """ Searches for the items submitted with specified content provider as the items' initial source.
    The source designates the initial item's source, not the service provider who submitted an item
    into the Echo Platform. The source filter defaults to all item sources.
    Compare this to the ProviderFilter.
    """
    def __init__(self, filter_values=[]):
        super(SourceFilter, self).__init__('source', filter_values=filter_values,
                                         allowable_values=SOURCE_FILTERS)

# NOTE: The "provider" filter values are application dependent.
PROVIDER_FILTERS = []
class ProviderFilter(QueryFilter):
    """ Searches for the items submitted by a service provider into the Echo platform (via submit).
    The provider defaults to all item service providers.
    Compare this to the SourceFilter. 
    """
    def __init__(self, filter_values=[]):
        super(ProviderFilter, self).__init__('provider', filter_values=filter_values,
                                         allowable_values=PROVIDER_FILTERS)

# NOTE: The "tags" filter values are application dependent.
TAGS_FILTERS = []
class TagsFilter(QueryFilter):
    """ Searches for the items tagged with the specified tags, defined strings.
    By default, all items are selected unless the tags search operator is specified.
    """
    def __init__(self, filter_values=[]):
        super(TagsFilter, self).__init__('tags', filter_values=filter_values,
                                         allowable_values=TAGS_FILTERS)

# NOTE: The "markers" filter values are application dependent.
MARKERS_FILTERS = []
class MarkersFilter(QueryFilter):
    """ Similar to tags, this searches for items with specified markers attached.
    Markers have the same meaning as tags except they only belong to some application namespace,
    to one or more applications owned by the same customer.
    By default, all items are selected unless the markers search operator is specified.
    """
    def __init__(self, filter_values=[]):
        super(MarkersFilter, self).__init__('markers', filter_values=filter_values,
                                         allowable_values=MARKERS_FILTERS)

# ======================================================================
# Safe HTML Filter
# ======================================================================

SAFE_HTML_FILTERS = [ 'aggressive', 'permissive', 'off' ]
class SafeHTMLFilter(QueryFilter):
    """ All data in ECHO is stored in the same form as it was submitted. But
    for safety and simplicity reasons it is usually sanitized before being returned
    in search results. The level of sanitization can be set using this parameter.

    The possible values are: [ 'aggressive', 'permissive', 'off' ]

    ``aggressive`` - Removes most HTML tags except for the specific list of known
    and safe ones. Retains embedded YouTube and Vimeo videos.

    ``permissive`` - Removes content of tag <script></script> and removes other
    explicitly dangerous tags (like iframe, frameset, etc).

    ``off`` - Disables any changes to the items content.
    """
    def __init__(self, filter_values=[]):
        super(SafeHTMLFilter, self).__init__('safeHTML', filter_values=filter_values,
                                         allowable_values=SAFE_HTML_FILTERS)

# ======================================================================
# User Filters: QueryFilter Subclasses with "user.*" applied.
# ======================================================================

# NOTE: The "user.id" filter value is an application dependent URL.
class UserIDFilter(QueryFilter):
    """ Searches for the items owned by a user with the specified user identity URI.
    By default, if this parameter is skipped, the items owned by any user are returned.
    """
    def __init__(self, identity_url):
        super(UserIDFilter, self).__init__('user.id', filter_values=identity_url,
                                            allowable_values=[])

# NOTE: The "user.markers" filter values are application dependent.
class UserMarkersFilter(QueryFilter):
    """ Searches for the items owned by the users marked with the specified marker(s).
    By default, if this parameter is skipped, items are returned regardless of the user markers.
    """
    def __init__(self, filter_values=[]):
        super(UserMarkersFilter, self).__init__('user.markers', filter_values=filter_values,
                                         allowable_values=MARKERS_FILTERS)

ROLES_FILTERS = [ "administrator", "moderator" ]
class UserRolesFilter(QueryFilter):
    """ Searches for the items owned by the users with the specified role(s).
    By default, if this parameter is skipped, items are returned regardless of the user roles.
    """
    def __init__(self, filter_values=[]):
        super(UserRolesFilter, self).__init__('user.roles', filter_values=filter_values,
                                         allowable_values=ROLES_FILTERS)

USER_STATE_FILTERS = [ 'Untouched', 'ModeratorDeleted', 'ModeratorBanned',
                       'ModeratorApproved' ]
class UserStateFilter(QueryFilter):
    """ Searches for the items owned by users with a given state.
    By default, if this parameter is skipped, items are returned regardless of the user state.
    """
    def __init__(self, filter_values=[]):
        super(UserStateFilter, self).__init__('user.state', filter_values=filter_values,
                                              allowable_values=USER_STATE_FILTERS)

# ======================================================================
# Children Depth Filter
# ======================================================================

class ChildrenDepth(QueryFilter):
    """ Depth of Child Items

    The search query sends back not only the item found, the "root item", but also some children of the item,
    "children items" in terms of Graph Database. This may be specified by the EQL, and if not specified, there is
    a default value of "depth=2".
    """
    def __init__(self, depth='2', itemsPerPage=None):
        # NOTE: Must convert depth to string type for __str__(): ','.join(...)
        super(ChildrenDepth, self).__init__('children', filter_values=str(depth))
        self.itemsPerPage = itemsPerPage

    def _allowable_value(self, value):
        try:
            int(value) # Must be able to cast as an integer.
        except (ValueError, TypeError):
            raise TypeError("%s: Invalid children depth %r" % (self.__class__.__name__, value))

    # ChildrenDepth cannot be negated.
    # Negative Filter: True == ON, False == OFF.
    def _get_negative(self): return False
    negative = property(_get_negative)

    def __str__(self):
        """ This EQL substring is added to a query. """
        eql_list = [ "%s:%s" % (self.filter_name, ','.join(self.filter_values)) ]
        if self.itemsPerPage:
            eql_list.append("%s:%s" % ('childrenItemsPerPage', self.itemsPerPage))
        return ' '.join(eql_list)

# ======================================================================
# Sort Order Filters:
# ======================================================================

ROOT_SORT_ORDERS = [
    "likesDescending",
    "repliesDescending",
    "flagsDescending",
    "chronological",
    "reverseChronological"
]
class RootSortOrder(QueryFilter):
    """ Controls the root node sort order for the query. """
    def __init__(self, sort_order="reverseChronological"):
        super(RootSortOrder, self).__init__('sortOrder', filter_values=[sort_order],
                                            allowable_values=CHILDREN_SORT_ORDERS)

CHILDREN_SORT_ORDERS = ["chronological", "reverseChronological"]
class ChildrenSortOrder(QueryFilter):
    """ Controls the sort order of the children retrieved from the query. """
    def __init__(self, sort_order="reverseChronological"):
        super(ChildrenSortOrder, self).__init__('childrenSortOrder', filter_values=[sort_order],
                                                allowable_values=CHILDREN_SORT_ORDERS)

# ======================================================================
# Compound Query Filters: AND, OR
# ======================================================================

class CompoundQueryFilter(object):
    def __init__(self, filter_a, filter_b, is_and=True):
        self.filter_a = filter_a
        self.filter_b = filter_b
        self.operator_str = 'AND' if is_and else 'OR'

    def __str__(self):
        return "(%s %s %s)" % (str(self.filter_a), self.operator_str, str(self.filter_b))

    def __repr__(self):
        return "Compound Filter: %s" % str(self)


# ======================================================================

if __name__ == "__main__":

    # TypeFilter test:
    type_filter = TypeFilter([ 'article', 'note' ])
    ## type_filter.negative = True
    print "[TYPE] %r OR %s" % (type_filter, str(type_filter))


    # ChildrenDepth test:
    depth = ChildrenDepth(4, itemsPerPage=21)
    ## depth.negative = True # illegal assignment
    print "[Children] %r OR %s" % (depth, str(depth))

    # Compound Query Filter test:
    print
    c = CompoundQueryFilter(type_filter, depth)
    print "[AND] %s" % str(c)
    d = CompoundQueryFilter(type_filter, depth, is_and=False)
    print "[OR] %s" % str(d)
    print
    print "Use '&' operator."
    and_filter = type_filter & -type_filter
    print "[Operator AND] %s" % str(and_filter)
    print
    print "Use '|' operator on compound AND."
    ## or_more_filter = type_filter | c
    or_more_filter = c | type_filter
    print "[Operator '|'] %s" % str(or_more_filter)

