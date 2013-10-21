#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging
from optparse import OptionParser
from httpcachepurger import HTTPCachePurger

def get_parser(host, port, strict, timeout):
    """ Setup parser options """
    parser = OptionParser(usage="%prog [-h|--help] [options] <url> [<url> [...]]")
    parser.add_option("-m", '--method', dest="method",
                      help="Cache purging method to use",
                      choices=["ban", "purge"], default="ban")
    parser.add_option('-d', '--hostname', dest='hostname',
                      help='purge cache for host HOST', metavar='HOST',
                      default=host)
    parser.add_option('-s', '--server', dest='server', default=None, 
                      help="connect to SERVER. If not present, HOST will be resolved" + \
                      "and used as server address", metavar="SERVER")
    parser.add_option('-p', '--port', dest='port',
                      help='connect to host port PORT', metavar='PORT',
                      default=port)
    parser.add_option('-t', '--timeout', dest='timeout',
                      help='blocking operations (like connection attempts) ' + \
                           'will timeout after TIMEOUT seconds',
                      metavar='TIMEOUT', default=timeout)
    parser.add_option('-S', '--strict', dest='strict', action='store_true',
                      help='force the connection to be strict: ' + \
                      'BadStatusLine is raised if the status line ' + \
                      'cannot be parsed as a valid HTTP/1.0 or 1.1 ' + \
                      'status line',
                      metavar="STRICT", default=strict)
    parser.add_option("-M", "--no-multiprocess", action="store_false", default=True,
                      help="Do not use multiprocessing (i.e. purge url sequentially)",
                     dest="multiprocessing")
    parser.add_option("-v", "--verbose", action="count", help="Increase " +\
                      "verbosity. Can be specified multiple times", dest="verbosity")

    return parser

def main():
    """ Main entrance point """
    parser = get_parser(host='localhost', port=80, strict=False, timeout=10)
    (opts, args) = parser.parse_args()
    level = logging.WARN if opts.verbosity == 0 else \
            logging.INFO if opts.verbosity == 1 else logging.DEBUG
    logging.basicConfig(level=level)
    if not args:
        parser.error("No urls to purge")

    client = HTTPCachePurger(opts.hostname, opts.server, opts.port, 
                             opts.strict, opts.timeout)
    meth = getattr(client, opts.method)
    results = meth(args, opts.multiprocessing)
    for result in results:
        logging.debug(result)
