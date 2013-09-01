"""Generic Card Class."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
from six import text_type


class Card(object):
    """
    The card stores general information about the card.
     * code: the unique identifier for this card.
     * name: name of this card to be displayed.
     * abilities: dict of phase ids containing a list of action descriptors.
     * attributes: list of special details this card has.
     * info: dict of any information you would like.

    Card can be saved to, and loaded from, a string. Call ``str()`` on a Card
    instance or ``.save_string()`` on the instance. This will return a string
    that when evaluated using ``eval()`` can be unpacked into the Card
    constructor re-create that card. For example.
    ``original = Card(1, 'cool card')``
    ``savestring = str(card)``
    ``loaded = Card(*eval(savestring))``
    ``assert loaded == original``
    """
    def __init__(self, code=None, name=None, loaddict=None):
        self.code = 0 if code is None else code
        self.name = '' if name is None else name
        self.abilities = {}
        self.attributes = []
        self.info = {}
        if loaddict is not None:
            self.load(loaddict)

    def is_valid(self):
        """Returns True if code is not 0 and self.name is not ''."""
        return self.code != 0 and self.name != ''

    def has_attribute(self, attribute):
        """Return true if this card contains the given attribute."""
        return attribute in self.attributes

    def add_attribute(self, attribute):
        """
        Add the given attribute to this Card. Returns the length of
        attributes after addition.
        """
        self.attributes.append(attribute)
        return len(self.attributes)

    def get_abilities(self, phase):
        """Returns an ability list for the given phase ID."""
        return self.abilities[phase] if phase in self.abilities else None

    def add_ability(self, phase, ability):
        """Add the given ability to this Card under the given phase. Returns
        the length of the abilities for the given phase after the addition.
        """
        if phase not in self.abilities:
            self.abilities[phase] = []
        self.abilities[phase].append(ability)
        return len(self.abilities[phase])

    def get_info(self, key):
        """Return a value in the info for this card with the given key."""
        return self.info[key] if key in self.info else None

    def set_info(self, key, value, append=True):
        """
        Set any special info you wish to the given key. Each info is stored in
        a list and will be appended to rather then overriden unless append is
        False.
        """
        if append:
            if key not in self.info:
                self.info[key] = []
            self.info[key].append(value)
        else:
            self.info[key] = value

    def save(self):
        """
        Converts the Card as is into a dictionary capable of reconstructing the
        card with ``Card.load`` or serialized to a string for storage.
        """
        return dict(code=self.code, name=self.name, abilities=self.abilities,
                    attributes=self.attributes, info=self.info)

    def load(self, carddict):
        """
        Takes a carddict as produced by ``Card.save`` and sets this card
        instances information to the previously saved cards information.
        """
        self.code = carddict["code"]
        if isinstance(self.code, text_type):
            self.code = eval(self.code)
        self.name = carddict["name"]
        self.abilities = carddict["abilities"]
        if isinstance(self.abilities, text_type):
            self.abilities = eval(self.abilities)
        self.attributes = carddict["attributes"]
        if isinstance(self.attributes, text_type):
            self.attributes = eval(self.attributes)
        self.info = carddict["info"]
        if isinstance(self.info, text_type):
            self.info = eval(self.info)
        return self

    def __eq__(self, other):
        """Return True if this card's code is the same as the other's code."""
        return isinstance(other, Card) and self.code == other.code

    def __neq__(self, other):
        """
        Return True if this card's code is not the same as the other's code.
        """
        return isinstance(other, Card) and self.code != other.code

    def __str__(self):
        """
        Called by ``str(MyCard)``. Returns a string that when given to
        ``eval()`` will produce a tuple that can be unpacked and given to the
        Card constructor to replicate this card.

        This is used for saving the card as a string representation of a
        carddict for later usage.
        """
        return str(self.save())

    def __repr__(self):
        """
        Called by ``repr(MyCard)``. Returns the string '<Card:#>' where '#'
        is replaced with the code for the card instance.
        """
        return "<Card:{0}>".format(str(self.code))
