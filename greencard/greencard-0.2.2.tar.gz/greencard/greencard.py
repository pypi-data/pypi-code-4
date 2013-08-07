"""Greencard implementation."""
from functools import wraps


TESTS = []


def greencard(func):
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


def descovery(testdir):
    """Descover and load greencard tests."""
    from os.path import join, exists, isdir, splitext, basename
    if not testdir or not exists(testdir) or not isdir(testdir):
        return None

    from glob import glob
    import imp

    for testpath in glob(join(testdir, "*.py")):
        name, _ = splitext(basename(testpath))
        imp.load_source('tests.{0}'.format(name), testpath)


RESULTS = """
Results:
{0} tests
{1} cards
{2} passes
{3} failures"""


def main(clargs=None):
    """Command line entry point."""
    from argparse import ArgumentParser
    from librarian.library import Library
    import sys

    parser = ArgumentParser(
        description="A test runner for each card in a librarian library.")
    parser.add_argument("library", help="Library database")
    parser.add_argument("-t", "--tests", default="./tests/",
                        help="Test directory")
    args = parser.parse_args(clargs)

    descovery(args.tests)

    library = Library(args.library)
    passes = 0
    failures = 0
    cardcount = 0

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
    print(RESULTS.format(len(TESTS), cardcount, passes, failures))
    sys.exit(failures)
