"""Generic Card Class."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import random
from functools import partial


class Deck(object):
    """A collection of possibly recuring cards stored as codes."""
    def __init__(self, library=None, cards=None):
        self.library = library
        self.cards = cards if cards is not None else []

    def remaining(self):
        """Returns the number of remaining cards in the deck."""
        return len(self.cards)

    def shuffle(self):
        """Sort the cards in the deck into a random order.."""
        self.cards = random.shuffle(self.cards)

    def get_card(self, index=-1, cache=True, remove=True):
        """
        Retrieve a card any number of cards from the top. Returns a
        ``Card`` object loaded from a library if one is specified otherwise
        just it will simply return its code.

        If `index` is not set then the top  card will be retrieved.

        If cache is set to True (the default) it will tell the library to cache
        the returned card for faster look-ups in the future.

        If remove is true then the card will be removed from the deck before
        returning it.
        """
        if len(self.cards) < index:
            return None

        retriever = self.cards.pop if remove else self.cards.__getitem__
        code = retriever(index)

        if self.library:
            return self.library.load_card(code, cache)
        else:
            return code

    def top_cards(self, number=1, cache=True, remove=True):
        """
        Retrieve the top number of cards as ``Librarian.Card`` objects in a
        list in order of top to bottom most card. Uses the decks
        ``.get_card`` and passes along the cache and remove arguments.
        """
        getter = partial(self.get_card(cache=cache, remove=remove))
        return [getter(index=i) for i in range(number)]

    def move_top_cards(self, other, number=1):
        """
        Move the top `number` of cards to the top of some `other` deck.

        By default only one card will be moved if `number` is not specified.
        """
        other.cards.append(reversed(self.cards[-number:]))

    def contains_card(self, code):
        """Returns true if the given code is currently stored in this deck."""
        return code in self.cards

    def contians_attribute(self, attribute):
        """
        Returns how many cards in the deck have the specified attribute.

        This method requires a library to be stored in the deck instance and
        will return `None` if there is no library.
        """
        if self.library is None:
            return 0

        load = self.library.load_card
        matches = 0
        for code in self.cards:
            card = load(code)
            if card.has_attribute(attribute):
                matches += 1
        return matches

    def contains_info(self, key, value):
        """
        Returns how many cards in the deck have the specified value under the
        specified key in their info data.

        This method requires a library to be stored in the deck instance and
        will return `None` if there is no library.
        """
        if self.library is None:
            return 0

        load = self.library.load_card
        matches = 0
        for code in self.cards:
            card = load(code)
            if card.get_info(key) == value:
                matches += 1
        return matches
