"""
sentry_uploads.scripts.runner
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2013 by Process Systems Enterprise.
:license: BSD, see LICENSE for more details.
"""

from __future__ import absolute_import

import logging
import os
import sys
import pwd
from optparse import OptionParser

from raven import Client
from sentry.utils.strings import compress

def read_encode(path):
    fh = open(path, 'rb')
    try:
        return compress(fh.read())
    finally:
        fh.close()

def main():
    root = logging.getLogger('sentry.errors')
    root.setLevel(logging.DEBUG)
    root.addHandler(logging.StreamHandler())

    parser = OptionParser()
    parser.add_option("--dsn", action="store", default = os.environ.get('SENTRY_DSN'))
    (opts, args) = parser.parse_args()

    if not opts.dsn:
        print "Error: No configuration detected!"
        print "You must either pass a DSN with --dsn or set the SENTRY_DSN environment variable."
        sys.exit(1)

    if not args:
        print "Error: no files specified!"
        print "You must pass at least one filename on the command line."
        sys.exit(1)

    client = Client(opts.dsn)
    client.string_max_length = None

    data = {
        'culprit': 'sentry_uploads.scripts.runner',
        'logger': 'sentry_uploads.test',
    }

    data.update({
        'sentry_uploads.interfaces.Uploads': {
            'files': [{
                'filename': os.path.basename(path),
                'data': read_encode(path),
            } for path in args],
        },
    })

    ident = client.get_ident(client.captureMessage(
        message = 'Upload of %s via sentry-upload script' % str(args),
        data = data,
        level = logging.INFO,
    ))

    if client.state.did_fail():
        print 'error!'
        return False

    print 'success!'
