#!/usr/bin/env python
# Module:   extractor
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Web Extraction Tool"""

import sys
from json import dumps
from os import environ, path
from time import clock, time
from functools import partial
from uuid import uuid4 as uuid
from collections import defaultdict
from multiprocessing.pool import ThreadPool
from optparse import OptionGroup, OptionParser

from lxml.html import tostring as doc_to_str

from . import __version__
from .utils import dict_to_text, doc_to_text, fetch_url, is_url, log, parse_html

try:
    from calais import Calais
    from .processors import process_calais
except ImportError:
    Calais = None  # NOQA

USAGE = "%prog [options] [file | url | -]"
VERSION = "%prog v" + __version__
DESCRIPTION = (
    "Tool to extract fragments of a given document by use of CSS Selector(s). "
    "Specify each input filter using the -f/--filter option as a key/value pair with an optional attribute that can be specified after the key. "
    "Example: -f \"key[.attribute]=expression\""
    "If - is provided as the only argument, then for each line of standard output "
    "(assumed to be a url) and the -o/--output option, extraction of each url "
    "will be processed and dumped to the given output path."
)


def calais_options(parser):
    group = OptionGroup(
        parser,
        "Open Calais Options",
        "These options can be used to perform text analysis "
        "with the OpenCalais (http://www.opencalais.com/) "
        "web service. You must specify --calais-key or set "
        "the environment variable CALAIS_KEY to your key."
    )

    group.add_option(
        "", "--calais",
        action="store_true", default=False, dest="calais",
        help="Perform OpenCalais Text Analysis"
    )

    group.add_option(
        "", "--calais-key",
        action="store", type="string", metavar="KEY", default=environ.get("CALAIS_KEY", ""), dest="calais_key",
        help="OpenCalais API Key"
    )

    parser.add_option_group(group)


def parse_options():
    parser = OptionParser(description=DESCRIPTION, usage=USAGE, version=VERSION)

    parser.add_option(
        "-f", "--filter",
        action="append", type="string", metavar="FILTER", default=None, dest="filters",
        help="A CSS selector in the form: key=expression"
    )

    parser.add_option(
        "-j", "--jobs",
        action="store", type="int", metavar="JOBS", default=None, dest="jobs",
        help="Specifies the number of jobs to run simultaneously. Defaults to the no. of CPU(s) on the system."
    )

    parser.add_option(
        "-o", "--output",
        action="store", type="string", metavar="PATH", default=None, dest="output",
        help="An output path to dump results"
    )

    parser.add_option(
        "-v", "--verbose",
        action="store_true", default=False, dest="verbose",
        help="Enable verbose logging"
    )

    if Calais is not None:
        calais_options(parser)

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    if args and args[0] == "-" and not opts.output:
        print("ERROR: -o/--output is required for when using standard input")
        parser.print_help()
        raise SystemExit(1)

    if opts.output is not None:
        opts.output = path.abspath(path.expanduser(opts.output))
        if not path.isdir(opts.output):
            print("ERROR: -o/--output must be a valid output path.")
            parser.print_help()
            raise SystemExit(1)

    return opts, args


def extract(source, filters):
    filters = dict(filter.split("=") for filter in filters)
    s = fetch_url(source)[1] if is_url(source) else open(source, "r").read()
    doc = parse_html(s)

    result = {}
    for k, v in filters.items():
        es = doc.cssselect(v)
        if "." in k:
            k, a = k.split(".")
            texts = htmls = [e.attrib.get(a, "") for e in es]
        else:
            htmls = [doc_to_str(e) for e in es]
            texts = [doc_to_text(e) for e in es]
        
        result["_{0:s}".format(k)] = htmls
        result[k] = texts
    return result


def job(opts, source):
    try:
        opts.verbose and log("Processing: {0:s}", source)

        result = extract(source, opts.filters)

        if Calais is not None and opts.calais:
            result.update(process_calais(dict_to_text(result), key=opts.calais_key))

        result["_source"] = source

        if opts.output is not None:
            with open(path.join(opts.output, "{0:s}.json".format(uuid())), "w") as f:
                f.write(dumps(result))
        else:
            print(dumps(result))
        return True, source
    except Exception as e:
        log("Error Processing {0:s} {1:s}", source, e)
        return False, source


def main():
    opts, args = parse_options()

    source = args[0]

    stime = time()

    sources = (line.strip() for line in sys.stdin) if source == "-" else (source,)

    pool = ThreadPool(opts.jobs)

    retries = defaultdict(int)

    while sources:
        results = pool.map(partial(job, opts), sources)
        [retries.pop(source, None) for success, source in results if success]
        retries.update((source, (retries[source] + 1)) for success, source in results if not success)
        sources = [source for source, tries in retries.items() if tries < 3]

    opts.verbose and log("Error(s):")
    [log(source) for source, tries in retries.items() if tries >= 3]

    cputime = clock()
    duration = time() - stime

    opts.verbose and log("Processed in in {0:0.2f}s using {1:0.2f}s of CPU time.", duration, cputime)


if __name__ == "__main__":
    main()
