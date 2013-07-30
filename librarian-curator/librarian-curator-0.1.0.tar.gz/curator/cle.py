"""Command Line Editor for cards with the Librarian API."""
from __future__ import print_function
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import os
import sys
from .console import Console


def clear():
    """Platform independent clear console screen."""
    if "windows" not in sys.platform.lower():
        os.system("clear")
    else:
        os.system("cls")


class CLE(Console):
    """The command line editor for cards."""
    def __init__(self, colormap, card):
        """
        Can take up to two arguments to define the code and name of the new
        card before starting the edit although it is optional.
        """
        Console.__init__(self)
        self.colormap = colormap
        self.card = card
        self.prompt = "{Csym}[{Ckey}EDIT{Csym}]>{Cres}".format(**self.colormap)

    def do_commit(self, _):
        """
        Save all changes and exit.
        """
        return -1

    def do_exit(self, _):
        """
        Exit without saving changes.
        """
        self.card = None
        return -1

    def do_code(self, args):
        """
        ``code <newcode>`` Set the card code to <newcode>.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            self.card.code = int(args[0])
        self.header()

    def do_name(self, args):
        """
        ``name <newname>`` Set the card name to <newname>.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            self.card.name = " ".join(args)
        self.header()

    def do_attribute(self, args):
        """
        ``attribute <attr>`` Add <attr> to this cards attributes.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            self.card.add_attribute(" ".join(args))
        self.header()

    def do_ability(self, args):
        """
        ``ability <phase> <abi>`` Add <abi> to this cards abilities under
        <phase>.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            if len(args) > 1:
                self.card.add_ability(args[0], " ".join(args[1:]))
        self.header()

    def do_info(self, args):
        """
        ``info <key> <data>`` Add <data> to this cards info under <key>.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            if len(args) > 1:
                self.card.set_info(args[0], " ".join(args[1:]), True)
        self.header()

    def do_delete(self, args):
        """
        ``delete <field> <key/index> <index>`` delete info from the card
        under field and if required key and/then the index. Use the display
        header to get index's.
        """
        if args:
            args = [arg.strip() for arg in args.split()]
            field = args[0]
            if field == "attribute" and len(args) >= 2:
                if len(self.card.attributes) <= int(args[1]):
                    del self.card.attributes[int(args[1])]
                return self.header()
            elif field == "attribute":
                self.card.attributes = []
                return self.header()
            elif field == "ability" and len(args) >= 3:
                if args[1] in self.card.abilities and \
                        len(self.card.attributes[args[1]]) >= int(args[2]):
                    del self.card.abilities[args[1]][int(args[2])]
                return self.header()
            elif field == "ability" and len(args) >= 2:
                if args[1] in self.card.abilities:
                    del self.card.abilities[args[1]]
                return self.header()
            elif field == "ability":
                self.card.abilities = {}
                return self.header()
            elif field == "info" and len(args) >= 3:
                if args[1] in self.card.info and \
                        len(self.card.info[args[1]]) >= int(args[2]):
                    del self.card.info[args[1]][int(args[2])]
                return self.header()
            elif field == "info" and len(args) >= 2:
                if args[1] in self.card.info:
                    del self.card.info[args[1]]
                return self.header()
            elif field == "info":
                self.card.info = {}
                return self.header()
        self.header()

    def header(self):
        """Display a header of card information."""
        clear()
        if self.card is None:
            return None
        card = self.card
        print("{Cval}{0}{Csym}: {Cval}{1}".format(card.code, card.name,
                                                  **self.colormap))

        print("{Csym}:::::{Ckey}Attributes".format(**self.colormap))
        for index, attr in enumerate(self.card.attributes):
            print("{Csym}[{Ckey}{0}{Csym}]{Ckey}{1}".format(str(index), attr,
                                                            **self.colormap))

        print("{Csym}:::::{Ckey}Abilities".format(**self.colormap))
        for phase, abilities in self.card.abilities.items():
            print("{Cval}{0}".format(phase, **self.colormap))
            for index, ability in enumerate(abilities):
                print("{Csym}|_____[{Ckey}{0}{Csym}]{Cval}{1}".format(
                    str(index), ability, **self.colormap))

        print("{Csym}:::::{Ckey}Info".format(**self.colormap))
        for key, value in self.card.info.items():
            print("{Cval}{0}".format(key, **self.colormap))
            for index, info in enumerate(value):
                print("{Csym}|_____[{Ckey}{0}{Csym}]{Cval}{1}".format(
                    str(index), info, **self.colormap))

    def preloop(self):
        """Display header at start."""
        Console.preloop(self)
        self.header()
