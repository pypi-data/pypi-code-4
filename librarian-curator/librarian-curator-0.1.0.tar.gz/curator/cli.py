"""Command Line Interface for the Librarian API."""
from __future__ import print_function
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import os
import sys
from colorama import Fore
from colorama import Style
from librarian.library import Library
from librarian.card import Card
from .console import Console
from .cle import CLE


def readinput(prefix):
    """Python version independent input reading."""
    if sys.version_info > (3, 0):
        return input(prefix)
    else:
        return raw_input(prefix)


def clear():
    """Platform independent clear console screen."""
    if "windows" not in sys.platform.lower():
        os.system("clear")
    else:
        os.system("cls")


class CLI(Console):
    """The command line inteface."""
    def __init__(self, dbname=None):
        """
        Takes a filename for the database and will create it and any required
        tables if the database filename doesnt exist.
        """
        Console.__init__(self)
        self.colormap = dict(Cval=Fore.YELLOW, Csym=Fore.GREEN, Ckey=Fore.CYAN,
                             Cres=Style.RESET_ALL)
        self.prompt = "{Csym}[{Ckey}HOME{Csym}]>{Cres}".format(**self.colormap)
        dbname = "library.lbr" if dbname is None else dbname
        self.library = Library(dbname)
        if not os.path.exists(dbname):
            self.library.create_db()
        self.list_max = 50

    def do_edit(self, args):
        """Edit a card. Can take a card code to edit."""
        code = int(args) if args else 0
        card = self.library.load_card(code, cache=False)
        if card is None:
            card = Card(code)

        cle = CLE(self.colormap, card)
        cle.cmdloop()
        card = cle.card

        if card is None:
            return clear()

        self.library.save_card(card)
        clear()

    def do_delete(self, args):
        """Delete a card by code."""
        if args:
            code = int(args)
        else:
            clear()
            print("Input code to delete.")
            code = int(readinput("|>"))

        with self.library.connection() as libdb:
            libdb.execute("DELETE from CARDS where code = {0}".format(code))

    def do_list(self, args):
        """List all stored cards. Can search by a code prefix."""
        code = args if args else None
        results = self.library.filter_search(code=code)

        if not len(results):
            print("No cards could be found")
            return None

        if len(results) > self.list_max:
            results = results[:self.list_max]

        for codename in results:
            print("{Cval}{0}{Csym}: {Cval}{1}".format(*codename,
                                                      **self.colormap))

    def do_setting(self, _):
        """Change settings for this session."""
        print("Maximum cards to return from list or search.")
        self.list_max = int(readinput("|>"))

    def do_search(self, _):
        """
        Perform an advanced card search. Input nothing to skip filter or '*'
        for an info or ability as a wildcard.
        """
        code = readinput("Code\n|>")
        if not code:
            code = None
        name = readinput("Name\n|>")
        if not name:
            name = None

        abilities = {}
        while True:
            print("Ability:")
            phase = readinput("Phase\n|>")
            if not phase:
                break
            ability = readinput("Ability\n|>")
            if not ability:
                ability = '*'
            abilities[phase] = ability
        if not abilities:
            abilities = None

        attributes = []
        while True:
            attrib = readinput("Attribute\n|>")
            if not attrib:
                break
            attributes.append(attrib)
        if not attributes:
            attributes = None

        info = {}
        while True:
            print("Info:")
            key = readinput("Key\n|>")
            if not key:
                break
            value = readinput("Value\n|>")
            if not value:
                value = '*'
            info[key] = value
        if not info:
            info = None

        results = self.library.filter_search(code, name, abilities, attributes,
                                             info)
        if not len(results):
            print("No cards could be found")
            return None

        if len(results) > self.list_max:
            results = results[:self.list_max]

        for codename in results:
            print("{Cval}{0}{Csym}: {Cval}{1}".format(*codename,
                                                      **self.colormap))
