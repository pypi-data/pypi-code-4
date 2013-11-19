#!/usr/bin/env python
# Module:   cralser
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""Crawler"""

import sys
from warnings import warn
from time import clock, time
from optparse import OptionParser

from collections import deque
from re import compile as compile_regex

from url import parse as parse_url

from . import __version__
from .utils import error, fetch_url, get_links, log, status

USAGE = "%prog [options] <url>"
VERSION = "%prog v" + __version__


HEADERS = {
    "User-Agent": "{0} v{1}".format(__name__, __version__)
}


def crawl(root_url, allowed_urls=None, blacklist=None, max_depth=0, patterns=None, verbose=False, whitelist=None):
    """Crawl a given url recursively for urls.

    :param root_url: Root URL to start crawling from.
    :type  root_url: str

    :param allowed_urls: A list of allowed urls (matched by regex) to traverse.
                         By default a regex is compiled for the ``root_url`` and used.
    :type  allowed_urls: list or None

    :param blacklist: A list of blacklisted urls (matched by regex) to not traverse.
    :type  blacklist: list or None

    :param max_depth: Maximum depth to follow, 0 for unlimited depth.
    :param max_depth: int

    :param patterns: A list of regex patterns to match urls against. If evaluates to ``False``, matches all urls.
    :type  patterns: list or None or False

    :param verbose: If ``True`` will print verbose logging
    :param verbose: bool

    :param whitelist: A list of whitelisted urls (matched by regex) to traverse.
    :type  whitelist: list or None

    :returns: A dict in the form {"error": set(...), "urls": set(...)}
              The errors set contains 2-item tuples of (status, url)
              The urls set contains 2-item tuples of (rel_url, abs_url)
    :rtype: dict

    In verbose mode the following single-character letters are used to denonate meaning for URLs being processed:
     - (I) (I)nvalid URL
     - (F) (F)ound a valid URL
     - (S) (S)een this URL before
     - (E) (E)rror fetching URL
     - (V) URL already (V)isitied
     - (B) URL blacklisted
     - (W) URL whitelisted

    Also in verbose mode each followed URL is printed in the form:
    <status> <reason> <type> <length> <link> <url>

    .. deprecated:: 0.0.2
       The ``allowed_url`` parameter has been deprecated in favor of two additional parameters
       ``blacklist`` and ``whitelist``.

    .. versionadded:: 0.0.2
       ``blacklist`` and ``whitelist`` control a regex matched pattern of urls to traverse.
    """

    blacklist = [compile_regex(regex) for regex in blacklist] if blacklist else []
    patterns = [compile_regex(regex) for regex in patterns] if patterns else []
    root_url = parse_url(root_url)
    queue = deque([root_url])
    visited = []
    errors = []
    urls = []
    n = 0
    l = 0

    # XXX: Remove this block in spyda>0.0.2
    if allowed_urls:
        warn("The use of the ``allowed_urls`` parameter is deprecated. Please use ``whitelist`` instead.", category=DeprecationWarning)
        if whitelist:
            whitelist.extend(allowed_urls)

    whitelist = [compile_regex(regex) for regex in whitelist] if whitelist else []

    while queue:
        try:
            if max_depth and n >= max_depth:
                break

            n += 1
            current_url = queue.popleft()
            _current_url = current_url.utf8()
            visited.append(_current_url)

            response, content = fetch_url(_current_url)

            if not response.status == 200:
                errors.append((response.status, _current_url))
                links = []
            else:
                links = list(get_links(content))

            verbose and log(
                " {0:d} {1:s} {2:s} {3:s} {4:d} {5:s}",
                response.status, response.reason,
                response["content-type"], response.get("content-length", ""),
                len(links), current_url.utf8()
            )

            for link in links:
                url = current_url.relative(link).defrag().canonical()
                _url = url.utf8()

                if _url in urls:
                    verbose and log("  (S): {0}", _url)
                    continue

                if url._scheme not in ("http", "https"):
                    verbose and log("  (I): {0}", _url)
                    continue

                if _url in visited:
                    verbose and log("  (V): {0}", _url)
                    continue

                if patterns and not any((regex.match(_url) is not None) for regex in patterns):
                    verbose and log("  (P): {0}", _url)
                else:
                    verbose and log("  (F): {0}", _url)
                    urls.append(_url)
                    l += 1

                if blacklist and any((regex.match(_url) is not None) for regex in blacklist):
                    if whitelist and any((regex.match(_url) is not None) for regex in whitelist):
                        queue.append(url)
                        verbose and log("  (W): {0}", _url)
                    else:
                        visited.append(_url)
                        verbose and log("  (B): {0}", _url)
                else:
                    queue.append(url)

            not verbose and status("Q: {0:d} F: {1:d} V: {2:d} L: {3:d}", len(queue), n, len(visited), l)
        except Exception as e:  # pragma: no cover
            error(e)
        except KeyboardInterrupt:  # pragma: no cover
            break

    return {
        "urls": urls,
        "errors": errors
    }


def parse_options():
    parser = OptionParser(usage=USAGE, version=VERSION)

    # XXX: Remove this block in spyda>0.0.2
    parser.add_option(
        "-a", "--allowed_url",
        action="append", default=None, dest="allowed_urls",
        help="(@deprecated) Allowed url to traverse (multiple allowed)."
    )

    parser.add_option(
        "-b", "--blacklist",
        action="append", default=None, dest="blacklist",
        help="Blacklisted URL to not traverse (multiple allowed)."
    )

    parser.add_option(
        "-d", "--max_depth",
        action="store", type=int, default=0, dest="max_depth",
        help="Maximum depth to follow (0 for unlimited)"
    )

    parser.add_option(
        "-p", "--pattern",
        action="append", default=None, dest="patterns",
        help="URL pattern to match (multiple allowed)."
    )

    parser.add_option(
        "-v", "--verbose",
        action="store_true", default=False, dest="verbose",
        help="Enable verbose logging"
    )

    parser.add_option(
        "-w", "--whitelist",
        action="append", default=None, dest="whitelist",
        help="Whitelisted URL to traverse (multiple allowed)."
    )

    opts, args = parser.parse_args()

    if len(args) < 1:
        parser.print_help()
        raise SystemExit(1)

    # XXX: Remove this block in spyda>0.0.2
    if opts.allowed_urls:
        warn("The use of the ``-a/--allowed_url`` option is deprecated. Please use ``-w/--whitelist`` instead.", category=DeprecationWarning)

    return opts, args


def main():
    opts, args = parse_options()

    url = args[0]

    if opts.verbose:
        print("Crawling {0:s}".format(url))

    stime = time()
    result = crawl(url, **opts.__dict__)

    if result["urls"]:
        if opts.verbose:
            print("URL(s):")
        print("\n".join(result["urls"]))
    else:
        if opts.verbose:
            print("No URL(s) found!")

    if result["errors"]:
        if opts.verbose:
            print >> sys.stderr, "Error(s):"
        print >> sys.stderr, "\n".join(
            " {0:d} {1:s}".format(*url) for url in result["errors"]
        )

    if opts.verbose:
        cputime = clock()
        duration = time() - stime
        urls = len(result["urls"])
        urls_per_second = int(urls / duration)

        print(
            "{0:d} urls in {1:0.2f}s ({2:d}/s) CPU: {3:0.2f}s".format(
                urls, duration, urls_per_second, cputime
            )
        )

if __name__ == "__main__":
    main()
