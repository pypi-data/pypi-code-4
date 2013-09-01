"""The Library class, an sqlite database of cards."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import sqlite3
from .card import Card


FIELDS = ("code", "name", "abilities", "attributes", "info")


def Where_filter_gen(*data):
    """
    Generate an sqlite "LIKE" filter generator based on the given data.
    This functions arguments should be a N length series of field and data
    tuples.
    """
    where = []

    def Fwhere(field, pattern):
        """Add where filter for the given field with the given pattern."""
        where.append("WHERE {0} LIKE '{1}'".format(field, pattern))

    def Fstring(field, string):
        """Add a where filter based on a string."""
        Fwhere(field, "%{0}%".format(string if not isinstance(string, str)
                                     else str(string)))

    def Fdict(field, data):
        """Add where filters to search for dict keys and values."""
        for key, value in data.items():
            if value == '*':
                Fstring(field, key)
            else:
                Fstring(field, "{0}:%{1}".format(key, value if not
                                                 isinstance(value, str)
                                                 else str(value)))

    def Flist(field, data):
        """Add where filters to search for elements of a list."""
        for elem in data:
            Fstring(field, elem if not isinstance(elem, str) else
                    str(elem))

    for field, data in data:
        if isinstance(data, str):
            Fstring(field, data)
        elif isinstance(data, dict):
            Fdict(field, data)
        elif isinstance(data, list):
            Flist(field, data)

    return ' AND '.join(where)


class Library(object):
    """
    Library wraps an sqlite3 database that stores serialized cards.

    Library also allows load and save hooks that allow a list of function to be
    called on each string as it is saved and loaded.

    The ``Library`` constructor can take a ``cardclass`` argument which
    defaults to ``librarian.card.Card`` and is used to construct a card object
    when loading. A ``cardclass`` should be a subclass of
    ``librarian.card.Card`` and be able to take the original ``carddict``
    constructor argument alone along with providing the original or equal
    ``Card.load`` and ``Card.save`` methods.
    """
    def __init__(self, dbname, cachelimit=100, cardclass=Card):
        self.dbname = dbname
        self.save_chain = []
        self.load_chain = []
        self.cachelimit = cachelimit
        self.card_cache = {}
        self.card_cache_list = []
        self.cardclass = cardclass

    def cached(self, code):
        """Return True if there is a card for the given code in the cache."""
        return code in self.card_cache[code]

    def cache_card(self, card):
        """
        Cache the card for faster future lookups. Removes the oldest card
        when the card cache stores more cards then this libraries cache limit.
        """
        code = card.code
        self.card_cache[code] = card
        if code in self.card_cache_list:
            self.card_cache_list.remove(code)
        self.card_cache_list.append(code)

        if len(self.card_cache_list) > self.cachelimit:
            del self.card_cache[self.card_cache_list.pop(0)]

    def create_db(self):
        """Create the CARDS table in the sqlite3 database."""
        with sqlite3.connect(self.dbname) as carddb:
            carddb.execute("""CREATE TABLE IF NOT EXISTS CARDS(code STRING,
            name STRING, abilities STRING, attributes STRING, info STRING)""")

    def load_card(self, code, cache=True):
        """
        Load a card with the given code from the database. This calls each
        save event hook on the save string before commiting it to the database.

        Will cache each resulting card for faster future lookups with this
        method while respecting the libraries cache limit. However only if the
        cache argument is True.

        Will return None if the card could not be loaded.
        """
        card = self.card_cache.get(code, None)
        if card is None:
            code = code if isinstance(code, str) else str(code)
            with sqlite3.connect(self.dbname) as carddb:
                result = carddb.execute(
                    "SELECT * FROM CARDS WHERE code = ?", (code,))
                loadrow = result.fetchone()
                if not loadrow:
                    return None
                loaddict = dict(zip(FIELDS, loadrow))
                card = self.cardclass(loaddict=loaddict)
            if cache:
                self.cache_card(card)
        return card

    def save_card(self, card, cache=False):
        """
        Save the given card to the database. This calls each save event hook
        on the save string before commiting it to the database.
        """
        if cache:
            self.cache_card(card)
        carddict = card.save()
        with sqlite3.connect(self.dbname) as carddb:
            carddb.execute("DELETE from CARDS where code = ?",
                           (carddict["code"],))
            carddb.execute("INSERT INTO CARDS VALUES(?, ?, ?, ?, ?)",
                           [carddict[key] if isinstance(carddict[key], str)
                            else str(carddict[key]) for key in FIELDS])

    def retrieve_all(self):
        """
        A generator that iterates over each card in the library database.

        This is best used in for loops as it will only load a card from the
        library as needed rather then all at once.
        """
        with sqlite3.connect(self.dbname) as carddb:
            for row in carddb.execute("SELECT code FROM CARDS"):
                yield self.load_card(row[0])

    def filter_search(self, code=None, name=None, abilities=None,
                      attributes=None, info=None):
        """
        Return a list of codes and names pertaining to cards that have the
        given information values stored.

        Can take a code integer, name string, abilities dict {phase: ability
        list/"*"}, attributes list, info dict {key, value list/"*"}.

        In the above argument examples "*" is a string that may be passed
        instead of a list as the dict value to match anything that stores that
        key.
        """
        command = "SELECT code, name FROM CARDS "
        command += Where_filter_gen(("code", code), ("name", name),
                                    ("abilities", abilities),
                                    ("attributes", attributes),
                                    ("info", info))

        with sqlite3.connect(self.dbname) as carddb:
            return carddb.execute(command).fetchall()

    def connection(self):
        """Connect to the underlying database and return the connection."""
        return sqlite3.connect(self.dbname)
