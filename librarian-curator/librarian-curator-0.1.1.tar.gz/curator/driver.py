"""Command line driver entry point."""
from __future__ import print_function
__version__ = "0.1.0"
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
from .cli import CLI
import colorama
import argparse
import sys


def main():
    """Drive the usage of curator-cli."""
    parser = argparse.ArgumentParser(
        description="library access from the command line.")
    parser.add_argument("-v", "--version", help="Display curator-cli version",
                        action="store_true", default=False)
    parser.add_argument("libname", help="Path to the librarian library file",
                        type=str, default="library.lbr")
    args = parser.parse_args()

    if args.version:
        print('curator-cli v'+__version__)
        sys.exit(0)

    colorama.init()
    CLI(args.libname).cmdloop()
