""" Echo Query Language

This is an object-oriented API for the Echo Query Language.
Build queries from terms and produce a valid EQL query string.

    q = Query("http://site.example.com/index.html", uri_filter='url')
    q.add_filter(filters.ChildrenDepth(3))
    q.add_filter(filters.TypeFilter('article'), negate=True)

    EQL> "url:"http://site.example.com/index.html" children:3 -type:article"

    q1 = Query("http://blog.example.com/movies//")
    q1 - filters.TypeFilter(['article', 'note'])

    EQL> "scope:"http://blog.example.com/movies/*" -type:article,note"
"""
from echo.eql import filters

URI_FILTER_TYPES = [ 'scope', 'childrenof', 'url']
WILD_CARD_TYPES = [ 'scope', 'childrenof' ]
SAFE_HTML_LEVELS = ['aggressive', 'permissive', 'off' ]

class QueryError(Exception):
    pass

class Query(object):
    """ Query objects compose an Items API query in the Echo Query Language.
    A Query object has a uri_path and one uri_filter, or Search Operator.
    This is the basic Search Query unit, and filter operators may be added.

    wild_card=True is the default, and add the '*' after 'scope' or 'childrenof'.
    """
    def __init__(self, uri_path, uri_filter='scope', wild_card=True):
        if uri_filter not in URI_FILTER_TYPES:
            raise QueryError("Invalid URI filter %r" % uri_filter)
        if wild_card and uri_filter in WILD_CARD_TYPES:
            self.uri_path = "%s/*" % uri_path.rstrip('/')
        else:
            self.uri_path = uri_path
        self.uri_filter = uri_filter
        self.filter_list = []

    def __str__(self):
        """ Return the composed EQL query string. """
        # Any URI containing '#' or '?' must be quoted, and this code quotes all URIs.
        # For example: 'scope:"http://example.com/path?x=1&y=2"'
        eql_list = [ '%s:"%s"' % (self.uri_filter, self.uri_path), ]
        eql_list.extend([ str(f) for f in self.filter_list ])
        return ' '.join(eql_list)

    def __repr__(self):
        return "EQL %s %r" % (self.__class__.__name__, self.__str__())

    def add_filter(self, filter, negate=False):
        """ Add another filter to this Query object, as the right-most one in the list.
        Also, use the operator methods, __add__ (+) and __sub__(-), to add a filter.
        Filters include Packaging & Representation Operators in echo.eql.filters.
        Programmers must add filters in the order desired.
        """
        if not isinstance(filter, filters.QueryFilter):
            TypeError("Filter must be type %r" % filters.QueryFilter.__name__)
        # Toggle f.negative flag based on composition.
        if negate:
            filter = filter.__neg__()
        self.filter_list.append(filter)

    def __add__(self,  filter):
        """ Add a filter to this Query.
        query + filter
        """
        # Compose in-line, no deep copy.
        self.add_filter(filter)
        return self

    def __sub__(self,  filter):
        """ Add a negated filter to this Query.
        query - filter # Query does not match this filter!
        """
        # Compose in-line, after a deep copy.
        self.add_filter(filter, negate=True)
        return self

    def __and__(self, query):
        """ Logical AND: Combine two, possibly filtered, Query objects using the & operator.
        (query1 + filter) & query2
        """
        # Overload '&' operator to produce AND.
        if not isinstance(query, (Query, CompoundQuery)):
            return TypeError("AND Compound Query needs Query, not %s" % query.__class__.__name__)
        return CompoundQuery(self, query, is_and=True)

    def __rand__(self, query):
        # NOTE: use "__rand__" so that CompoundQuery can be first operand.
        return self.__and__(query)

    def __or__(self, query):
        """ Logical OR: Combine two, possibly filtered, Query objects using the | operator.
        query1 | (query2 - filter)
        """
        # Overload '|' operator to produce OR.
        if not isinstance(query, (Query, CompoundQuery)):
            return TypeError("OR Compound Query needs Query, not %s" % query.__class__.__name__)
        return CompoundQuery(self, query, is_and=False)

    def __ror__(self, query):
        # NOTE: use "__ror__" so that CompoundQueryFilter can be first operand.
        return self.__or__(query)

# ======================================================================
# Compound Query: AND, OR
# ======================================================================

class CompoundQuery(object):
    def __init__(self, query_a, query_b, is_and=True):
        self.query_a = query_a
        self.query_b = query_b
        self.operator_str = 'AND' if is_and else 'OR'
        self.filter_list = []

    def __str__(self):
        eql_list = ["(%s %s %s)" % (str(self.query_a), self.operator_str, str(self.query_b))]
        eql_list.extend([str(f) for f in self.filter_list])
        return ' '.join(eql_list)

    def __repr__(self):
        return "Compound Query: %s" % str(self)

    def add_filter(self, filter, negate=False):
        """ Add another filter to this CompoundQuery object, as the right-most one in the list.
        Also, use the operator methods, __add__ (+) and __sub__(-), to add a filter.
        Filters include Packaging & Representation Operators in echo.eql.filters.
        Programmers must add filters in the order desired.
        """
        if not isinstance(filter, filters.QueryFilter):
            TypeError("Filter must be type %r" % filters.QueryFilter.__name__)
        # Toggle f.negative flag based on composition.
        if negate:
            filter = filter.__neg__()
        self.filter_list.append(filter)

    def __add__(self,  filter):
        """ Add a filter to this CompoundQuery.
        query + filter
        """
        # Compose in-line, no deep copy.
        self.add_filter(filter)
        return self

    def __sub__(self,  filter):
        """ Add a negated filter to this CompoundQuery.
        query - filter # CompoundQuery does not match this filter!
        """
        # Compose in-line, after a deep copy.
        self.add_filter(filter, negate=True)
        return self

# ======================================================================
# Representation Operators
# Safe HTML wraps the main Query object to choose the output format.
# ======================================================================

class SafeHTML(object):
    """ All data in ECHO is stored in the same form as it was submitted.
    For safety and simplicity reasons, it is sanitized before being returned in search results.
    The level of sanitization can be set using this parameter.
    The possible values are: [' aggressive', 'permissive', 'off' ]

    'aggressive': Remove most HTML tags except for the specific list of known and safe ones
                  (a, img, div, span, p, b, i, u, sub, sup, em, strong, pre, br, param, embed,).
                  Retains embedded YouTube and Vimeo videos.
    'permissive': Remove content of tag <script></script> and other explicitly dangerous tags (like iframe, frameset, etc).
    'off': Disables any changes to the items' content.

    query = Query("http://www.example.com/")
    safe_query = SafeHTML(query, 'permissive')
    """
    def __init__(self, query, level='aggressive'):
        if not isinstance(query, (Query, CompoundQuery)):
            raise TypeError("SafeHTML needs Query, not %s" % query.__class__.__name__)
        self.query = query
        if level not in SAFE_HTML_LEVELS:
            raise QueryError("Invalid %s is %s. Choose one of: %r" % (self.__class__.__name__, level, SAFE_HTML_LEVELS))
        self.level = level

    def __str__(self):
        """ Return the EQL query term after all the others. """
        return "%s safeHTML:%s" % (str(self.query), self.level)

    def __repr__(self):
        return str(self)

# ======================================================================

if __name__ == "__main__":
    q = Query("http://site.example.com/index.html", uri_filter='url')
    q.add_filter(filters.ChildrenDepth(3))
    q.add_filter(filters.TypeFilter('article'), negate=True)
    print "EQL> ", q

    # Use filter operators on Query object...
    q1 = Query("http://blog.example.com/movies//")
    ## q1 = q1 - filters.TypeFilter(['article', 'note'])
    q1 - filters.TypeFilter(['article', 'note'])
    print "EQL> ", q1

    # Compound Query OR
    print
    print "[OR] EQL> ", (q & q1) | q

    # safeHTML
    print "safeHTML Samples..."
    print "EQL> ", SafeHTML(q1)
    print
    print "[OR] EQL> ", SafeHTML(q | q1)

