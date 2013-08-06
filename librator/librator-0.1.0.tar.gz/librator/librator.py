"""Command line entry points."""
from argparse import ArgumentParser
from os.path import splitext, exists, dirname
from os import makedirs
from .packing import pack, unpack


def main(clargs=None):
    """The primary entry point, can pack or unpack a **Librarian** library."""
    parser = ArgumentParser(
        description="Handles Librarian card database packaging.")
    parser.add_argument("cards", type=str,
                        help="Directory of single .crd card files")
    parser.add_argument("library", type=str,
                        help="Library database file")
    parser.add_argument("-u", "--unpack", action="store_true", default=False,
                        help="Unpack existing library")
    args = parser.parse_args(clargs)

    if not exists(dirname(args.cards)):
        if args.unpack:
            makedirs(dirname(args.card))
        else:
            print("cards directory not found!")
            return None
    if args.unpack and not exists(args.library):
        print("library database not found!")
        return None

    if args.unpack:
        unpack(args.library, args.cards)
    else:
        pack(args.library, args.cards)


CARDTEMPLATE = """
name: card
code: 0
attributes:
- alive
abilities:
  open:
  - attack
info:
  art:
  - ""
"""


def cardmain(clargs=None):
    """Generate a blank card file."""
    parser = ArgumentParser(
        description="Create a black card file template.")
    parser.add_argument("cardfile", type=str,
                        help="Card filename")
    args = parser.parse_args(clargs)

    filename, _ = splitext(args.cardfile)
    filename += ".crd"

    with open(filename, "w") as cardfile:
        cardfile.write(CARDTEMPLATE.strip())
