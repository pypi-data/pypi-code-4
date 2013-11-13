#!/usr/bin/env python

import os
import sys
import subprocess
import optparse
from datetime import date

"""
Automatically apply licenses to a folder.
"""
__author__ = "michaelb"
__copyright__ = "Copyright 2013"
__credits__ = ["michaelb"]
__license__ = "GPL"
__version__ = "0.0.1"
__email__ = "michaelpb@gmail.com"

LICENSES = [
        'GPL 3.0',
        'LGPL 3.0',
        'MIT',
        'Apache 2.0',
        'BSD 3 Clause',
        'BSD 2 Clause',
        'GPL 2.0',
        'LGPL 2.1',
        'zlib',
    ]
    

LICENSES_PATH = os.path.join(os.path.dirname(__file__), "licenses")


####################################################################
# Terminal output functions
# A few functions for making output to the terminal neater
####################################################################
class Term:
    bold = "\033[1m"
    reset= "\033[0;0m"
    purple = '\033[95m'
    blue = '\033[94m'
    green = '\033[92m'
    yellow = '\033[93m'
    red = '\033[91m'
    Bold = staticmethod(lambda s: Term.bold + s + Term.reset)
    Blue = staticmethod(lambda s: Term.blue + s + Term.reset)
    Yellow = staticmethod(lambda s: Term.yellow + s + Term.reset)
    Green = staticmethod(lambda s: Term.green + s + Term.reset)
    Red = staticmethod(lambda s: Term.red + s + Term.reset)
    Purple = staticmethod(lambda s: Term.purple + s + Term.reset)

def warning(msg):
    sys.stderr.write(Term.Yellow("Warning: ") + Term.Bold(msg) + "\n")

def trace(msg, arg=''):
    sys.stdout.write(Term.Blue("---> ") + msg + ((" "+Term.Purple(arg)) if arg else '') + "\n")


def error(msg):
    sys.stderr.write(
            Term.Red(sys.argv[0]) + ": " +
            Term.Red("Error") + ": " +
            Term.Bold(msg) + "\n")
    sys.exit(1)


def parse_options(string=None):
    """Support for command line options"""
    parser = optparse.OptionParser(version="%%prog %s" % __version__)

    parser.add_option(
        "-v", "--verbose", action="count", dest="verbose",
        help="Show debug messages")

    parser.add_option(
        "-l", "--license",   dest="license", metavar="LICENSE", default="GPL 3.0",
        help="Use the given license.")

    parser.add_option(
        "-a", "--author",  dest="author", metavar="AUTHOR",
        help="Name of author. (will default git or hg name)")

    parser.add_option(
        "-t", "--list", action="store_true", dest="list",
        help="List all available licenses.")

    parser.add_option(
        "-y", "--year",  dest="year", metavar="YYYY",
        help="Year to use in (C) notice (current year is default).")

    parser.add_option(
        "-n", "--name",  dest="name", metavar="FILENAME", default="LICENSE",
        help="Filename to store in. (LICENSE is default.)")


    parser.add_option(
        "-f", "--force", action="store_true", dest="force",
        help="Overwrite current license.")

    (options, args) = parser.parse_args(sys.argv)

    return options, args

def search(output, begin, delim='='):
    for line in output:
        if line.strip().startswith(begin):
            _, _, name = line.partition(delim)
            return name
    return ''

def run(cmd):
    return subprocess.check_output(cmd, shell=True).splitlines()

def get_author():
    author = ''
    try:
        output = run('git config --list')
        author = search(output, 'user.name')
    except OSError:
        try:
            output = run('hg showconfig')
            author = search(output, 'ui.username')
        except OSError:
            pass

    return author

def err(s):
    sys.stderr.write("%s: %s\n" % (sys.argv[0], s))
    sys.exit(1)


def get_license(license_text):
    cleaned = lambda s: s.strip('.01').replace(' ', '').lower().replace('-', '')
    c_text = cleaned(license_text)
    matches = []
    for license_r in LICENSES:
        c_r = cleaned(license_r)
        if c_text == c_r:
            # exact match, return
            return license_r

        if c_text in c_r:
            matches.append(license_r)

    if matches:
        return matches[0]
    else:
        return ''

def get_year():
    return unicode(date.today().year)

def license_name_to_fn(name):
    return name.lower().replace(' ', '_') + ".txt"

def render_license_text(name, ctx):
    path = os.path.join(LICENSES_PATH, license_name_to_fn(name))
    with open(path, 'r') as f:
        text = f.read()
    return text % ctx

def main():
    opts, args = parse_options()

    if len(args) > 1:
        error("This takes no positional arguments. Check -h/--help for help.")


    if opts.list:
        for license_name in LICENSES:
            print(license_name)
        sys.exit(0)

    author = opts.author or get_author()

    if not author:
        error("Author not specified (use --author, or setup git / hg properly)")

    if opts.verbose:
        trace("Author:", author)

    year = opts.year or get_year()

    if opts.verbose:
        trace("Year:", year)

    license = get_license(opts.license)

    if not license:
        error(("Could not find license match for '%s'." % opts.license)+
            "Use --list to see options.")

    if opts.verbose:
        trace("License:", license)

    destination = opts.name

    if os.path.exists(destination) and not opts.force:
        error("'%s' exits. Use -f to overwrite." % destination)

    if opts.verbose:
        trace("Writing to:", destination)

    text = render_license_text(license, {
            'year': year,
            'author': author,
        })

    if destination.strip() == '-':
        print(text)
    else:
        with open(destination, 'w+') as f:
            f.write(text)


if __name__=='__main__':
    main()



