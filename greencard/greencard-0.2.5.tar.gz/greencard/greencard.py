"""Greencard implementation."""
from functools import wraps


TESTS = []
SINGLES = []


def card(func):
    """
    A decorator for providing a unittesting function/method with every card in
    a librarian card library database when it is called.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        """Transparent wrapper."""
        return func(*args, **kwargs)
    TESTS.append(wrapped)
    return wrapped


def library(func):
    """
    A decorator for providing a unittest with a library and have it called only
    once.
    """
    @wraps(func)
    def wrapped(*args, **kwargs):
        """Transparent wrapper."""
        return func(*args, **kwargs)
    SINGLES.append(wrapped)
    return wrapped


def descovery(testdir):
    """Descover and load greencard tests."""
    from os.path import join, exists, isdir, splitext, basename, sep
    if not testdir or not exists(testdir) or not isdir(testdir):
        return None

    from os import walk
    import fnmatch
    import imp

    for root, _, filenames in walk(testdir):
        for filename in fnmatch.filter(filenames, '*.py'):
            path = join(root, filename)
            modulepath = splitext(root)[0].replace(sep, '.')
            imp.load_source(modulepath, path)


def execute_tests(library):
    """
    Runs the library through each single test and each card in the library
    through each card test then returns ``(cardcount, passes, failures)``.
    """
    passes = 0
    failures = 0
    cardcount = 0

    for test in SINGLES:
        failed = False
        try:
            test(library)
        except AssertionError:
            print("Library failed {0}".format(test.__name__))
            failed = True
        if failed:
            failures += 1
        else:
            passes += 1

    for card in library.retrieve_all():
        cardcount += 1
        failed = False
        for test in TESTS:
            try:
                test(card)
            except AssertionError:
                print("{0} failed {1}".format(card.__repr__(), test.__name__))
                failed = True
        if failed:
            failures += 1
        else:
            passes += 1
    return cardcount, passes, failures


RESULTS = """
Results:
{0} library tests
{1} card tests
{2} cards
{3} passes
{4} failures"""


def main(clargs=None):
    """Command line entry point."""
    from argparse import ArgumentParser
    from librarian.library import Library
    import sys

    parser = ArgumentParser(
        description="A test runner for each card in a librarian library.")
    parser.add_argument("library", help="Library database")
    parser.add_argument("-t", "--tests", default="test/",
                        help="Test directory")
    args = parser.parse_args(clargs)

    descovery(args.tests)

    library = Library(args.library)
    cardcount, passes, failures = execute_tests(library)
    print(RESULTS.format(len(SINGLES), len(TESTS), cardcount, passes,
                         failures))
    sys.exit(failures)
