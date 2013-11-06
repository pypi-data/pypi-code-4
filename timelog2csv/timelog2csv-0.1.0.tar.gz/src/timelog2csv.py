#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""timelog2csv - converts a TimeLog calendar to a CSV file

TimeLog was a time tracking application for OS X. It stored it's data
using iCal. OS X Mountain Lion (and Mavericks) dropped some features
that TimeLog needed to talk to iCal. So it's impossible to access the
recorded data because the application won't even start.

But this small tool can help: Export the iCal calendar which you used to
store TimeLog's data. Then use timelog2csv to convert it to a CSV file.

Usage:
    timelog2csv [-h] [--project=<name> ...] <ical> <csv>
    timelog2csv --version

Options:
    -h --help              Show this help
       --version           Show version
       --project=<name>    Filter by project name

"""
from __future__ import unicode_literals

import codecs
import csv
import os
import sys

from docopt import docopt
from icalendar import Calendar

__author__ = 'Markus Zapke-Gründemann'
__email__ = 'markus@keimlink.de'
__version__ = '0.1.0'

try:
    from cStringIO import StringIO
except ImportError:
    from io import StringIO
try:
    from urllib import unquote
    from urlparse import urlparse, parse_qs
except ImportError:
    from urllib.parse import urlparse, parse_qs, unquote

if sys.version[0] == '3':
    raw_input = input

DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'


class UnicodeWriter:
    """A CSV writer which will write rows to CSV file "f".

    File "f" is encoded in the given encoding.
    """
    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        """Writes the ``row`` parameter to the writer’s file object."""
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        """Writes all the ``rows`` parameters to the writer’s file object."""
        for row in rows:
            self.writerow(row)


def parse_url(url):
    """Parses ``url`` into six components, returns components and query string.

    All query string key/value pairs are unquoted.
    """
    comp = urlparse(url, scheme='timelog')
    query = parse_qs(comp.query)
    for key, value in list(query.items()):
        query[key] = unquote(value[0])
        # client data must be reencoded
        if key == 'client':
            query[key] = query[key].encode('iso-8859-1').decode('utf-8')
    return comp, query


def get_row(component):
    """Returns a row created from a VEVENT ``component``.

    A row is a list consisting of eight elements:

        * client
        * project
        * category
        * description
        * start
        * end
        * duration
        * status
    """
    url_comp, query = parse_url(component['URL'])
    row = [query['client']]
    row.extend(component['summary'].split(':'))
    row.append(component['description'])
    start = component['dtstart'].dt
    row.append(start.strftime(DATETIME_FORMAT))
    end = component['dtend'].dt
    row.append(end.strftime(DATETIME_FORMAT))
    row.append(str(int((end - start).total_seconds() / 60)))
    if query['status'] == '(null)':
        row.append('')
    else:
        row.append(query['status'])
    return row


def read_data(ical_in, projects=None):
    """Reads the data from the iCal file, returns a list of rows.

    The optional argument ``projects`` can be used to filter the rows by
    project name.
    """
    data = []
    cal = Calendar.from_ical(ical_in.read())
    for component in cal.walk('VEVENT'):
        row = get_row(component)
        if not projects or row[1] in projects:
            data.append(row)
    return data


def check_source(filename):
    """Checks if the source file exists."""
    if not os.path.exists(filename):
        sys.stderr.write('Error: iCal file "%s" not found.\n' % filename)
        sys.exit(1)


def check_target(filename):
    """Checks if the target file exists.

    If the target file exists a confirmation to overwrite is required.
    """
    if os.path.exists(filename):
        sys.stdout.write('CSV file "%s" already exists.\n' % filename)
        answer = None
        while answer not in ('n', 'y'):
            answer = raw_input('Continue and overwrite the existing file? (yN) ')
            answer = answer.lower().strip()
            if len(answer) == 0:
                answer = 'n'
        if answer == 'n':
            sys.stdout.write('Aborted.\n')
            sys.exit()


def write_csv(csv_out, data, header=None):
    """Writes ``data`` to a CSV file.

    The ``header`` argument can be used to add a header row.
    """
    if header:
        data = [header] + data
    writer = UnicodeWriter(csv_out, delimiter=b';')
    writer.writerows(data)
    sys.stdout.write('Created CSV file "%s" with %d rows.\n' % (csv_out.name, len(data)))


def main():
    """Runs the main program."""
    args = docopt(__doc__, version=__version__)
    check_source(args['<ical>'])
    check_target(args['<csv>'])
    data = read_data(open(args['<ical>'], 'rb'), args['--project'])
    header = ['Client', 'Project', 'Category', 'Description', 'Start', 'End',
        'Duration', 'Status']
    with open(args['<csv>'], 'wb') as target:
        write_csv(target, data, header)


if __name__ == '__main__':
    main()
