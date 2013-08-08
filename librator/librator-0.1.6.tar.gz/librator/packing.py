"""Implementation of packing and unpacking functions."""
import yaml
from glob import glob
from os.path import join as pjoin
import os
from librarian.card import Card
from librarian.library import Library


def pack(library, carddir):
    """Pack all ``.crd`` card files in the carddir into the given library."""
    if os.path.exists(library):
        os.remove(library)

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
    if not os.path.exists(carddir) or not os.path.isdir(carddir):
        os.makedirs(carddir)

    lib = Library(library)
    cardpath = pjoin(carddir, "{0}.crd")

    for card in lib.retrieve_all():
        with open(cardpath.format(card.code), 'w') as cardfile:
            yaml.dump(card.save(), cardfile, default_flow_style=False)
