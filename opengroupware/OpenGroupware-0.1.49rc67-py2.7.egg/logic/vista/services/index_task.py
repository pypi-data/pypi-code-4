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


def index_task(task, context):

    stream = StringIO()

    keywords = archived = event_date = None

    stream.write(' {0} '.format(task.name))

    if task.state == '30_archived':
        archived = True
    else:
        archived = False

    keywords = parse_keywords(task.keywords, delimiter=' ')

    event_date = task.end

    stream.write(normalize_string(str(task.object_id)))
    stream.write(normalize_string(normalize_string(task.name)))
    stream.write(normalize_string(normalize_string(task.keywords)))
    stream.write(normalize_string(normalize_string(task.comment)))

    for note in task.notes:
        if note.comment:
            stream.write(normalize_string(note.comment))
        if note.action_date > event_date:
            event_date = note.action_date

    subindex_properties(task, context, stream)

    return keywords, archived, event_date, stream.getvalue()
