"""Data set generators."""
__author__ = 'Taylor "Nekroze" Lawson'
__email__ = 'nekroze@eturnilnetwork.com'
import random
from string import printable
import sys


# Constants
MIN_INT = -sys.maxsize - 1
MAX_INT = sys.maxsize
MIN_FLOAT = -1e7
MAX_FLOAT = 1e7
LIST_LEN = 30


# Basic Types
def Value(val):
    """
    Returns a generator that will endlessly spew out the same value.
    """
    while True:
        yield val


def Choice(choices):
    """
    Returns a generator that will endlessly spew out a random choice.
    """
    while True:
        yield random.choice(choices)


def String(least=0, most=LIST_LEN, valid=printable):
    """
    Returns a generator that will endlessly pump out random strings of a length
    >= least and <= most, constiting of strings/chars from the valid selection.

    The valid argument should be a list of string or a string of characters and
    defaults to all printable characters as defined in ``string.printable``.
    """
    while True:
        length = random.randint(least, most)
        yield ''.join([random.choice(valid) for _ in range(length)])


def Integer(least=MIN_INT, most=MAX_INT):
    """
    Returns a generator that endlessly returns random integers >= lest and <=
    most.
    """
    while True:
        yield random.randint(least, most)


def Float(least=MIN_FLOAT, most=MAX_FLOAT):
    """
    Returns a generator that endlessly returns random floats >= lest and <=
    most.
    """
    while True:
        yield random.uniform(least, most)


def Boolean():
    """
    Returns a generator that endlessly returns random True or False values.
    """
    while True:
        yield random.choice((True, False))


# Collections
def List(element, least=1, most=LIST_LEN):
    """
    Returns a generator that yields random lists from the given element
    generator. Lists can be given a upper and lower bound length.
    """
    while True:
        length = random.randint(least, most)
        yield [next(element) for _ in range(length)]


def Tuple(*args):
    """
    Returns a generator that yields random tuples of the given element
    generator of the given length.

    Arguments defined after the length are assumed to be generators used for
    values to store in the returned tuples.
    """
    while True:
        yield tuple([next(element) for element in args])


def Dictionary(gendict):
    """
    Returns a generator that endlessly yields dictionaries with the given keys
    and values derived from a dictionary of value generators.
    """
    while True:
        yield {key: next(val) for key, val in gendict.items()}
