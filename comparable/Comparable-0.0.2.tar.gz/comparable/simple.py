#!/usr/bin/env python

"""
Class definitions for simple comparable types.
"""

import logging
from difflib import SequenceMatcher

from comparable import SimpleComparable


class _Simple(SimpleComparable):  # pylint: disable=W0223
    """SimpleComparable with common magic methods implemented."""

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return self._repr(self.value)

    def __str__(self):
        return str(self.value)

    def __float__(self):
        return float(self.value)


class Number(_Simple):
    """Comparable positive number."""

    threshold = 0.999  # 99.9% similar

    def __init__(self, value):
        super().__init__(value)
        if value < 0:
            raise ValueError("Number objects can only be positive")

    def equality(self, other):
        """Get equality using floating point equality.
        """
        return float(self) == float(other)

    def similarity(self, other):
        """Get similarity as a ratio of the two numbers.
        """
        numerator, denominator = sorted((self.value, other.value))
        try:
            ratio = float(numerator) / denominator
        except ZeroDivisionError:
            ratio = 0.0 if numerator else 1.0
        similarity = self.Similarity(ratio)
        return similarity


class Text(_Simple):
    """Comparable generic text."""

    threshold = 0.83  # "Hello, world!" ~ "hello world"

    def equality(self, other):
        """Get equality using string comparison.
        """
        return str(self) == str(other)

    def similarity(self, other):
        """Get similarity as a ratio of the two texts.
        """
        ratio = SequenceMatcher(a=self.value, b=other.value).ratio()
        similarity = self.Similarity(ratio)
        return similarity


class TextEnum(Text):
    """Comparable case-insensitive textual enumeration."""

    threshold = 1.0  # enumerations must match

    def similarity(self, other):
        """Get similarity as a discrete ratio (1.0 or 0.0).
        """
        ratio = 1.0 if (str(self).lower() == str(other).lower()) else 0.0
        similarity = self.Similarity(ratio)
        return similarity


class TextTitle(Text):
    """Comparable case-insensitive textual titles."""

    threshold = 0.93  # "The Cat and the Hat" ~ "cat an' the hat"

    ARTICLES = 'a', 'an', 'the'  # stripped from the front
    JOINERS = '&', '+'  # replaced with 'and'

    def __init__(self, value):
        super().__init__(value)
        self.stripped = self._strip(self.value)
        logging.debug("stripped {} to {}".format(repr(self.value),
                                                 repr(self.stripped)))

    @staticmethod
    def _strip(text):
        """Strip articles/whitespace and remove case.
        """
        text = text.strip()
        text = text.replace('  ', ' ')  # remove duplicate spaces
        text = text.lower()
        for joiner in TextTitle.JOINERS:
            text = text.replace(joiner, 'and')
        for article in TextTitle.ARTICLES:
            if text.startswith(article + ' '):
                text = text[len(article) + 1:]
                break
        return text

    def similarity(self, other):
        """Get similarity as a ratio of the stripped text.
        """
        logging.debug("comparing {} and {}...".format(repr(self.stripped),
                                                      repr(other.stripped)))
        ratio = SequenceMatcher(a=self.stripped, b=other.stripped).ratio()
        similarity = self.Similarity(ratio)
        return similarity
