#!/usr/bin/env python
# coding=utf-8

"""logic for CLI. For both shell based command and REPL.

"""

import sys

from cloudns.utils import fargs
from cloudns.cli_utils import out, err
from cloudns.base import (RecordNotFound, DuplicateRecord, CloudnsError)


def print_cloudns_error(e):    # pylint: disable=C0103
    """print cloudns error.

    Args:
        e: should be a CloudnsError instance.

    """
    err(u"%s: %s\n", e.__class__.__name__, fargs(e.args))


def run_search(zone, args):
    """run search subcommand.

    This function do param checking and printing. It raises SystemExit when
    there is an error.

    Args:
        zone: the Zone object.
        args: a list of arguments for search.

    """
    if len(args) != 1:
        err(u"Error: search should be called with 1 argument.\n")
        sys.exit(1)
    try:
        r = zone.search_record(args[0])
        if r:
            out(u"%s record(s).\n", len(r))
            for record in r:
                out(u"%s\n", record.pretty_print())
        else:
            out(u"No record found.\n")
    except CloudnsError as e:
        print_cloudns_error(e)
        sys.exit(1)


def run_delete(zone, args):
    """run delete subcommand.

    For argument document and notes, see `run_search'.

    """
    if len(args) != 1:
        err(u"Error: delete should be called with 1 argument.\n")
        sys.exit(1)
    try:
        zone.delete_records_by_name(args[0], auto_retry=True)
    except RecordNotFound:
        out(u"No record found, nothing is deleted.\n")
    except CloudnsError as e:
        print_cloudns_error(e)
        sys.exit(1)


def run_create(zone, args):
    """run create subcommand.

    For argument document and notes, see `run_search'.

    """
    if len(args) < 3 or len(args) > 5:
        err(u"Error: create should be called with 3-5 arguments.\n")
        sys.exit(1)
    try:
        zone.create_record(*args)
    except DuplicateRecord:
        out(u"Record not created as it already exists.\n")
    except CloudnsError as e:
        print_cloudns_error(e)
        sys.exit(1)
