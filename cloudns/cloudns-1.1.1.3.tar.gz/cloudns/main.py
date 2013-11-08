#!/usr/bin/env python
# coding=utf-8

"""cloudns - a CLI interface for cloudns api

It can be used in two way, interactively as a REPL or as a shell command.

To run it as a REPL, do not pass a subcommand.

supported subcommand:

    create label content (tel|uni) [type [ttl]]
    search keyword            //fuzzy match, support *
    delete label              //exact match, delete all records with given label

Updating existing record is not supported. You have to delete then create.

"""

import sys
import logging

from cloudns.zone import Zone
from cloudns.base import logger
from cloudns.utils import fargs
from cloudns.cli_utils import out, warn, err
from cloudns.cli_logic import run_search, run_create, run_delete
from cloudns.repl import CloudnsREPL


DEFAULT_CONFIG_FILE = '~/.config/cloudns.conf'
KNOWN_COMMANDS = ("create", "search", "delete",
                  # aliases, not recommended for end user. not documented in
                  # help string.
                  "add", "new", "remove", "drop"
)
KNOWN_ZONES = ('game.yy.com', 'yygamedev.com', 'game.duowan.com',
               'yyclouds.com')

logger.setLevel(logging.WARNING)


def start_repl(args=None):
    repl = CloudnsREPL()
    if args:
        repl.passport = args.passport
        repl.token = args.token
        repl.zone = args.zone
    repl.cmdloop()


def run_subcommand(args):
    """run subcommand.

    Args:
        args: the parser object. check main() for what it contains.

    """
    if not (args.passport and args.token and args.zone):
        err(u"Error: passport/token/zone are all required.")
        sys.exit(1)
    zone = Zone.create_zone(args.passport, args.token, args.zone)
    if args.cmd in ("create", "add", "new"):
        run_create(zone, args.args)
    elif args.cmd == "search":
        run_search(zone, args.args)
    elif args.cmd in ("delete", "remove", "drop"):
        run_delete(zone, args.args)
    else:
        err(u"Error: subcommand %s not supported.\n", args.cmd)
        sys.exit(1)


def _parse_config_file(full_fn):
    """parse given config file.

    Return a dict that may contain key PASSPORT and TOKEN.

    """
    import re
    result = {}
    pattern = re.compile(r'^([_A-Z]+)=(.*)$')
    try:
        with open(full_fn, 'rb') as f:
            for line in f:
                line = line.decode('utf-8')
                r = pattern.match(line)
                if r:
                    result[r.group(1)] = r.group(2)
        return result
    except EnvironmentError as e:
        err(u"Error when reading config file %s: %s\n",
            full_fn, fargs(e.args))
        sys.exit(1)


def parse_config_file(args):
    """update parser by reading value from config file maybe.

    This method may modify the passed in param in place.

    Args:
        args: a ArgumentParser object.

    Return: None

    """
    import os

    if args.passport and args.token:
        return
    config_file = args.config_file or DEFAULT_CONFIG_FILE
    full_fn = os.path.abspath(os.path.expanduser(config_file))
    if os.path.exists(full_fn):
        params = _parse_config_file(full_fn)
        args.passport = args.passport or params.get('PASSPORT')
        args.token = args.token or params.get('TOKEN')
    else:
        if args.config_file:
            err(u"Error: config file not found: %s\n", full_fn)
            sys.exit(1)
        # ignore non-existing default config file.


def main(args=None):
    import argparse
    parser = argparse.ArgumentParser(
        prog='cloudns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__)
    parser.add_argument(
        '-f', '--config-file',
        help=u"load given config file instead of default [%s]" % (
            DEFAULT_CONFIG_FILE,))
    parser.add_argument('--passport', help=u"passport used for auth")
    parser.add_argument('--token', help=u"token used for auth")
    parser.add_argument('-z', '--zone', help=u"the zone to run command on")
    parser.add_argument('cmd', metavar='subcommand', nargs='?')
    parser.add_argument('args', metavar='arg', nargs='*')
    args = parser.parse_args(args)
    parse_config_file(args)
    if args.zone:
        if args.zone not in KNOWN_ZONES:
            warn(u"Warning: zone \"%s\" is not known to cloudns \
at the moment.\n", args.zone)
    if args.cmd:
        if args.cmd not in KNOWN_COMMANDS:
            err(u"Unkown sub command: %s\n", args.cmd)
            sys.exit(1)
        run_subcommand(args)
    else:
        start_repl(args)


if __name__ == '__main__':
    main()
