"""
The MIT License (MIT)

Copyright (c) 2013 Lunar Technology Corporation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
"""
import pyes

KEYWORD_LOWERCASE_NAME = 'keyword_lowercase'
LOWERCASE_FILTER = 'lowercase'
KEYWORD_TOKENIZER = 'keyword'
STRING_TYPE = 'string'
DATE_TYPE = 'date'
GEOPOINT_TYPE = 'geo_point'

INDEX_ANALYZED = 'analyzed'
INDEX_NOT_ANALYZED = 'not_analyzed'
INDEX_NOT_SEARCHED = 'no'


class SearchField(object):
    def __init__(self, field_type, analyzer=None, index=INDEX_ANALYZED):
        self.type = field_type
        self.analyzer = analyzer
        self.index = index

    def to_dict(self):
        d = dict(type=self.type)
        if self.analyzer:
            d['analyzer'] = self.analyzer
        if self.index:
            d['index'] = self.index
        return d


class SearchAnalyzer(object):
    def __init__(self, filters, tokenizer, analyzer_type=None, name=None):
        self.filters = filters
        self.tokenizer = tokenizer
        self.analyzer_type = analyzer_type or "custom"
        self.name = name

    def to_dict(self):
        return dict(
            filter=self.filters,
            type=self.analyzer_type,
            tokenizer=self.tokenizer
            )


KEYWORD_LOWERCASE = SearchAnalyzer(
    filters=[LOWERCASE_FILTER, ],
    tokenizer=KEYWORD_TOKENIZER,
    name=KEYWORD_LOWERCASE_NAME
    )


STANDARD_SETTINGS = {
    "analysis": {
        "analyzer": {
            KEYWORD_LOWERCASE.name: KEYWORD_LOWERCASE.to_dict()
            }
        }
    }

EXACT_MATCH_FIELD = SearchField(
    field_type=STRING_TYPE,
    index=INDEX_NOT_ANALYZED
    )

CASE_INSENSITIVE_EXACT = SearchField(
    field_type=STRING_TYPE,
    analyzer=KEYWORD_LOWERCASE.name
    )

DATE_FIELD = SearchField(field_type=DATE_TYPE)

GEO_FIELD = SearchField(field_type=GEOPOINT_TYPE)


class TextSearch(object):
    filter = False

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        return pyes.TextQuery(self.name, value, type="phrase_prefix", operator="and")


class ExactMatch(object):
    filter = True

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        return pyes.TermFilter(self.name, value)


class CaseInsensitiveExact(object):
    filter = False

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        q = pyes.FieldQuery()
        q.add(self.name, value.lower())
        return q


class CaseInsensitivePrefix(object):
    filter = False

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        q = pyes.PrefixQuery()
        q.add(self.name, value.lower())
        return q


class AfterDateQuery(object):
    filter = False

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        return pyes.RangeQuery(
            qrange=pyes.ESRange(
                self.name,
                from_value=value
                ))


class BeforeDateQuery(object):
    filter = False

    def __init__(self, name):
        self.name = name

    def for_value(self, value):
        return pyes.RangeQuery(
            qrange=pyes.ESRange(
                self.name,
                to_value=value
                ))


class StringQuery(object):
    filter = False

    def for_value(self, value):
        return pyes.StringQuery(value)
