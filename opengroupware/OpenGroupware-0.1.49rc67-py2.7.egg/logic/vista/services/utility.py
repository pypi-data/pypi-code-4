#
# Copyright (c) 2013
#  Adam Tauno Williams <awilliam@whitemice.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#
from StringIO import StringIO


def normalize_string(value):
    if value:
        if isinstance(value, list):
            return ' '.join(value).lower()
        elif isinstance(value, basestring):
            return ' {0} '.format(value.lower().strip())
    return ''


def normalize_datetime(value):
    if value:
        return ' {0} '.format(value.strftime('%Y-%m-%d %H:%M'))
    else:
        return ''


def parse_keywords(value, delimiter=' '):
    keywords = list()
    if value:
        if isinstance(keywords, basestring):
            keywords = [x.strip().lower()
                        for x in value.split(delimiter)
                        if len(x) < 128]
        elif isinstance(value, list):
            keywords = [x.strip().lower()
                        for x in value
                        if len(x) < 128]
    return keywords


def subindex_properties(entity, context, stream):
    for prop in context.property_manager.get_properties(entity):
        value = prop.get_value()
        if value:
            stream.write(normalize_string(str(value)))
    return True
