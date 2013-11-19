#!/usr/bin/env python

"""Entity Matching Tool"""

from glob import glob
from time import clock, time
from json import dumps, loads
from functools import partial
from operator import itemgetter
from optparse import OptionParser
from multiprocessing.pool import Pool

from . import __version__
from .utils import fetch_url, is_url, get_close_matches, log

USAGE = "%prog [options] [ data | url ] [ sources ]"
VERSION = "%prog v" + __version__
DESCRIPTION = (
    "Tool to perform entity matching given an input data source and a set of source files. "
    "Specify each match keys using the -m/--match option as a comma separated list of keys. "
    "Example: -m \"first_name,last_name\" "
    "Each set of match keys is joined by a single space and used as a data set to perform "
    "the entity matches again. If multiple match keys are provided then the first matching "
    "entity found that matches any of the data sets is used."
)


def parse_options():
    parser = OptionParser(description=DESCRIPTION, usage=USAGE, version=VERSION)

    parser.add_option(
        "-c", "--cutoff",
        action="store", type="float", metavar="NUM", default=0.85, dest="cutoff",
        help="A cutoff in range [0.0, 1.0] affecting the closness of matches."
    )

    parser.add_option(
        "-m", "--match-keys",
        action="append", type="string", metavar="MATCH-KEYS", default=None, dest="match_keys",
        help="A comma separated list of keys to match against"
    )

    parser.add_option(
        "-j", "--jobs",
        action="store", type="int", metavar="JOBS", default=None, dest="jobs",
        help="Specifies the number of jobs to run simultaneously. Defaults to the no. of CPU(s) on the system."
    )

    parser.add_option(
        "-o", "--output-key",
        action="store", type="string", metavar="KEY", default="entities", dest="output_key",
        help="An output key to store the matching entities"
    )

    parser.add_option(
        "-s", "--source-key",
        action="store", type="string", metavar="KEY", default="entities", dest="source_key",
        help="A source key to perform entity matching against in the sources"
    )

    parser.add_option(
        "-u", "--uri-key",
        action="store", type="string", metavar="KEY", default="uri", dest="uri_key",
        help="A URI key to use for populating matched entites to a unique URI"
    )

    parser.add_option(
        "-v", "--verbose",
        action="store_true", default=False, dest="verbose",
        help="Enable verbose logging"
    )

    opts, args = parser.parse_args()

    if len(args) < 2:
        parser.print_help()
        raise SystemExit(1)

    if not opts.match_keys:
        print("ERROR: At least one -m/--match-keys must be a specified.")
        parser.print_help()
        raise SystemExit(1)

    opts.match_keys = list(tuple((x.strip() for x in match_key.split(",") if x)) for match_key in opts.match_keys)

    return opts, args


def build_datasets(opts, source):
    records = loads(fetch_url(source)[1] if is_url(source) else open(source, "rb").read())
    return list(dict(("{0:s} {1:s}".format(*itemgetter(*keys)(record)), record[opts.uri_key]) for record in records) for keys in opts.match_keys)


def job(opts, datasets, source):
    try:
        opts.verbose and log("Processing: {0:s}", source)

        data = loads(open(source, "rb").read())
        source_entities = data.get(opts.source_key, [])

        matched_entities = []

        for entity in source_entities:
            for dataset in datasets:
                matches = get_close_matches(entity, dataset.keys(), cutoff=opts.cutoff)
                match, score = matches[0] if matches else (None, None)
                if match is not None:
                    matched_entities.append((match, score, dataset[match]))
                    break

        data[opts.output_key] = list({"name": match, "score": score, "uri": uri} for name, score, uri in matched_entities)

        open(source, "wb").write(dumps(data))

        return True, source
    except Exception as e:
        log("Error Processing {0:s} {1:s}", source, e)
        return False, source


def main():
    opts, args = parse_options()

    datasets = build_datasets(opts, args[0])
    sources = glob(args[1])

    stime = time()

    pool = Pool(opts.jobs)

    pool.map(partial(job, opts, datasets), sources)

    cputime = clock()
    duration = time() - stime

    opts.verbose and log("Processed in in {0:0.2f}s using {1:0.2f}s of CPU time.", duration, cputime)


if __name__ == "__main__":
    main()
