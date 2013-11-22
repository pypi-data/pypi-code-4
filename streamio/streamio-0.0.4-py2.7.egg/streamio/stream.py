# Module:   stream
# Date:     18th December 2012
# Author:   James Mills, j dot mills at griffith dot edu dot au

"""stream"""


import csv
import zlib
import struct
from time import time
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


def compress(iterable, level=9, encoding="utf-8"):
    """Compress the given iterable of bytes using zlib compressin

    :param iterable: An iterable of bytes to compress using zlib (ZIP)
    :type iterable: An iterable of ``bytes`` (If ``str`` will be encoded)

    :param level: An optional Compression Level
    :type level: ``int`` (Default: 9)

    :param encoding: An optional encoding to use when dealing with an iterable of ``str``
    :type encoding: ``str`` (Default: utf-8)

    :returns: An iterable compressed with zlib
    :rtype: iterable stream of ``bytes``
    """

    # See http://www.gzip.org/zlib/rfc-gzip.html
    yield b"\x1f\x8b"       # ID1 and ID2: gzip marker
    yield b"\x08"           # CM: compression method
    yield b"\x00"           # FLG: none set

    # MTIME: 4 bytes
    yield struct.pack("<L", int(time()) & int('FFFFFFFF', 16))
    yield b"\x02"           # XFL: max compression, slowest algo
    yield b"\xff"           # OS: unknown

    crc = zlib.crc32(b"")
    size = 0
    zobj = zlib.compressobj(level,
                            zlib.DEFLATED, -zlib.MAX_WBITS,
                            zlib.DEF_MEM_LEVEL, 0)
    for chunk in iterable:
        if not isinstance(chunk, bytes):
            chunk = chunk.encode(encoding)

        size += len(chunk)
        crc = zlib.crc32(chunk, crc)
        yield zobj.compress(chunk)
    yield zobj.flush()

    # CRC32: 4 bytes
    yield struct.pack("<L", crc & int('FFFFFFFF', 16))
    # ISIZE: 4 bytes
    yield struct.pack("<L", size & int('FFFFFFFF', 16))


__all__ = ("stream", "csvstream", "csvdictstream", "jsonstream", "compress",)
