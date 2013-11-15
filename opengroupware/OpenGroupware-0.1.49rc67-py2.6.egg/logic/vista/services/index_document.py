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
from utility import \
    normalize_string, \
    normalize_datetime, \
    parse_keywords, \
    subindex_properties


def index_document(document, context):

    stream = StringIO()

    keywords = archived = event_date = None

    if document.status == 'archived':
        archived = True
    else:
        archived = False

    event_date = document.modified

    keywords = list()

    stream.write(normalize_string(document.name))
    stream.write(normalize_string(str(document.object_id)))
    stream.write(normalize_string(document.abstract))
    stream.write(normalize_string(document.get_file_name()))
    stream.write(normalize_string(document.ogo_uri))
    if document.checksum:
        stream.write(normalize_string(document.checksum))

    subindex_properties(document, context, stream)

    return keywords, archived, event_date, stream.getvalue()
