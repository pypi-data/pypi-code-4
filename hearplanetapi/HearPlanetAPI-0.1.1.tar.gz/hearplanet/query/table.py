"""
HearPlanet table queries
"""

from read import Read

DEFAULT_LIMIT = 10

class Table(Read):
    def __init__(self, api, path, params={}):
        self.cached_schema = None
        Read.__init__(self, api, path, params)

    def search(self):
        self.path += '/search'
        return self

    def featured(self):
        self.path += '/featured'
        return self

    def fetch(self, pkey, objects=None, size=None):
        self.path += '/%s' % pkey
        if objects: self.path += '/%s' % objects
        if objects == 'images' and size: self.path += '/%s' % size
        return self

    def short(self):
        self.path += '/short'
        return self

    def term(self, terms):
        return self._copy({'q':terms})

    def location(self, location_str):
        return self._copy({'loc':location_str})

    def point(self, point):
        return self._copy({'lat':point['lat'], 'lng':point['lng']})

    def depth(self, depth):
        valid_values = ('min', 'poi', 'article', 'section',
                'section_text', 'all',)
        if depth not in valid_values:
            raise ValueError('depth must be one of %s', valid_values)
        return self._copy({'depth':depth})

    def filters(self, filters):
        return self._copy(filters)

    def format(self, format):
        valid_values = ('HTML', 'HTML-RAW', 'XHTML', 'PLAIN', 'AS-IS',)
        if format not in valid_values:
            raise ValueError('format must be one of %s', valid_values)
        return self._copy({'section_format':format})

    def limit(self, max_rows):
        assert max_rows >= 0
        return self._copy({'limit':max_rows})

    def offset(self, offset):
        return self._copy({'start':offset})

    def page(self, page_num, limit=DEFAULT_LIMIT):
        try:
            limit = self.params['limit'] if limit > 1 else DEFAULT_LIMIT
        except:
            limit = DEFAULT_LIMIT if limit < 1 else limit
        page_num = 1 if page_num < 1 else page_num
        return self.offset((page_num - 1) * limit).limit(limit)

    def schema(self):
        if not self.cached_schema:
            self.cached_schema = self.api.schema(self)
        return self.cached_schema

    def _copy(self, params):
        return Table(self.api, self.path, self.merge_params(params))

