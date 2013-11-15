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
import traceback
from StringIO import StringIO
from utility import \
    normalize_string, \
    normalize_datetime, \
    parse_keywords, \
    subindex_properties


def index_note(note, context):

    stream = StringIO()

    keywords = archived = event_date = None

    if note.status == 'archived':
        archived = True
    else:
        archived = False

    event_date = note.modified

    keywords = list()

    stream.write(normalize_string(note.title))
    stream.write(normalize_string(str(note.object_id)))
    stream.write(normalize_string(note.abstract))

    try:
        if note.content:
            text = note.content.encode('ascii', 'xmlcharrefreplace')
            stream.write(text)
    except UnicodeDecodeError, e:
        context.send_administrative_notice(
            subject=(
                'Content encoding error indexing noteId#{0}'.
                format(note.object_id, )
            ),
            message='{0}\n{1}'.format(e, traceback.format_exc()),
            urgency=4,
            category='document')

    subindex_properties(note, context, stream)

    return keywords, archived, event_date, stream.getvalue()
