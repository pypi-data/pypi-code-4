"""Implementation of packing and unpacking functions."""
import yaml
from glob import glob
from os.path import join as pjoin
from librarian.card import Card
from librarian.library import Library


def pack(library, carddir):
    """Pack all ``.crd`` card files in the carddir into the given library."""
    lib = Library(library)
    lib.create_db()

    for cardpath in glob(pjoin(carddir, "*.crd")):
        # Open card file and load it with yaml
        with open(cardpath) as cardfile:
            carddict = yaml.safe_load(cardfile)
        # Load the card dict from file into a card object
        card = Card().load(carddict)
        # Save the card object to the library
        lib.save_card(card)


def unpack(library, carddir):
    """Unpack all cards from the given library into carddir as .crd files."""
    lib = Library(library)
    cardpath = pjoin(carddir, "{0}.crd")

    for code, _ in lib.filter_search():
        card = lib.load_card(code)

        with open(cardpath.format(code), 'w') as cardfile:
            yaml.dump(card.save(), cardfile, default_flow_style=False)
