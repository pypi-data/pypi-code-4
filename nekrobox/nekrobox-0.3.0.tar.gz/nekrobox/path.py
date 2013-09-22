import os
from six.moves import range
from types import GeneratorType
from .docdecs import params


@params(path=(str, "Deepest absoulte path to start in"),
        returns=(GeneratorType, "Yields all paths above the given path"))
def backpaths(path):
    """Get all above paths.

    Return a generator of each path that makes up the given path. Essentially
    walking up the tree of directories from the given directory.

    The give path should be an absolute path.
    """
    paths = path.split(os.sep)[1:]
    for i in reversed(range(len(paths) + 1)):
        yield '/' + os.sep.join(paths[:i])


@params(filename=(str, "Filename to be checked for"),
        path=(str, "Absolute path to start in the search in"),
        checkhome=(bool, "Check home directory first"),
        returns=(list, "Filename matches from path backwards"))
def backsearch(filename, path, checkhome=True):
    """Backwards search for a filename.

    Search for the given `filename` in every directory above the given `path`.
    Return a list of any matches to the `filename` in these paths.
    """
    output = set()

    if checkhome and os.getenv("HOME"):
        home = os.path.join(os.getenv("HOME"), filename)
        if os.path.exists(home):
            output.add(home)

    for path in backpaths(path):
        checkpath = os.path.join(path, filename)

        if os.path.exists(checkpath):
            output.add(checkpath)

    return list(output)
