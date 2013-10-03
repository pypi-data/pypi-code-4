#!/usr/bin/env python

"""
Class definitions for compound comparable types.
"""

import logging
from itertools import permutations

from comparable import CompoundComparable


class Group(CompoundComparable):  # pylint: disable=W0223
    """Comparable list of Comparable items."""

    equality_list = None  # created dynamically
    similarity_dict = None  # created dynamically

    def __init__(self, items):
        self.items = items
        names = ["item{0}".format(n + 1) for n in range(len(items))]
        self.equality_list = names
        self.similarity_dict = {name: 1 for name in names}

    def __getattr__(self, name):
        """Allows self.items[<i>] to be accessed as self.item<i+1>.
        """
        if name.startswith('item'):
            try:
                index = int(name[4:]) - 1  # "item<n>" -> <n>-1
                return self[index]
            except ValueError:
                logging.debug("{} is not in the form 'item<n>'".format(name))
            except IndexError:
                logging.debug("item index {} is out of range".format(index))

        raise AttributeError

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def equality(self, other):
        """Calculate equality based on equality of all group items.
        """
        if not len(self) == len(other):
            return False
        return super().equality(other)

    def similarity(self, other):
        """Calculate similarity based on similarity of the best matching
        permutation of items.
        """
        # Select the longer list as the basis for comparison
        if len(self.items) > len(other.items):
            first, second = self, other
        else:
            first, second = other, self
        items = list(first.items)  # backup items list
        length = len(items)
        sim = self.Similarity(0.0 if length else 1.0)

        # Calculate the similarity for each permutation of items
        cname = self.__class__.__name__
        self.log(first, second, '%', cname=cname, aname='items')
        for permutation in permutations(items, length):
            first.items = permutation
            logging.debug("permutation: {}".format(first.items))
            sim = max(sim, super(Group, first).similarity(second))
            logging.debug("highest similarity: {}".format(sim))
        self.log(first, second, '%', cname=cname, aname='items', result=sim)
        first.items = items  # restore original items list

        return sim
