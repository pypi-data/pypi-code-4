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

KEYWORD_LOWERCASE = {
    "filter": ["lowercase"],
    "type": "custom",
    "tokenizer": "keyword"
    }

STANDARD_SETTINGS = {
    "analysis": {
        "analyzer": {
            "keyword_lowercase": KEYWORD_LOWERCASE
            }
        }
    }

EXACT_MATCH_FIELD = {
    "type": "string",
    "index": "not_analyzed"
    }

CASE_INSENSITIVE_EXACT = {
    "type": "string",
    "analyzer": "keyword_lowercase"
    }

DATE_FIELD = {
    "type": "date",
    }

GEO_FIELD = {
    "type": "geo_point",
    }


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
