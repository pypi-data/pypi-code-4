# Module:   stream
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""stream"""


import csv
from json import loads
from string import strip


from py._path.local import LocalPath
from funcy import compact, imap, zipdict


def stream(filename, skipblank=True, strip=True, stripchars="\r\n\t "):
    """Stream every line in the given file.

    :param filename: A ``str`` filename, A ``py._path.local.LocalPath`` instance or open ``file`` instnace.
    :type filename:  ``str``, ``py._path.local.LocalPath`` or ``file``.

    :param skipblank: Whehter to skip blank lines (sometimes undesirable)
    :type skipblank: ``bool``

    :param strip: Whehter to strip lines of surrounding whitespace (sometimes undesirable)
    :type strip: ``bool``

    :param stripchars: An iterable of characters to strip from the surrounding line. ``line.strip(...)`` is used.
    :type stripchars: ``list``, ``tuple`` or ``str``

    Each line in the file is read, stripped of surrounding whitespace and returned iteratively. Blank lines are ignored.
    """

    if isinstance(filename, LocalPath):
        fd = filename.open("rU")
    elif isinstance(filename, str):
        fd = open(filename, "rU")
    else:
        fd = filename

    for line in fd:
        line = line.strip(stripchars) if strip else line
        if line or not skipblank:
            yield line


def csvstream(filename):
    """Stream every line in the given file interpreting each line as CSV.

    :param filename: A ``str`` filename, A ``py._path.local.LocalPath`` instance or open ``file`` instnace.
    :type filename:  ``str``, ``py._path.local.LocalPath`` or ``file``.

    This is a wrapper around ``stream`` where the stream is treated as CSV.
    """

    if isinstance(filename, LocalPath):
        fd = filename.open("rU")
    elif isinstance(filename, str):
        fd = open(filename, "rU")
    else:
        fd = filename

    sniffer = csv.Sniffer()
    dialect = sniffer.sniff(fd.readline())
    fd.seek(0)

    reader = csv.reader(stream(fd, stripchars="\r\n"), dialect)
    for item in reader:
        yield item


def csvdictstream(filename, fields=None):
    """Stream every line in the given file interpreting each line as a dictionary of fields to items.

    :param filename: A ``str`` filename, A ``py._path.local.LocalPath`` instance or open ``file`` instnace.
    :type filename:  ``str``, ``py._path.local.LocalPath`` or ``file``.

    This is a wrapper around ``csvstream`` where the stream is treated as dict of field(s) to item(s).
    """

    stream = csvstream(filename)

    if fields is None:
        fields = map(strip, next(stream))

    for values in stream:
        yield compact(zipdict(fields, values))


def jsonstream(filename):
    """Stream every line in the given file interpreting each line as JSON.

    :param filename: A ``str`` filename, A ``py._path.local.LocalPath`` instance or open ``file`` instnace.
    :type filename:  ``str``, ``py._path.local.LocalPath`` or ``file``.

    This is a wrappedaround ``stream`` except that it wraps each line in a ``dumps`` call essentially treating
    each line as a piece of valid JSON.
    """

    return imap(loads, stream(filename))


__all__ = ("stream", "csvstream", "csvdictstream", "jsonstream",)
